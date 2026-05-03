import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from tqdm import tqdm

def train_model():
    """Train MobileNetV2 model with enhanced augmentation (Aim 1)"""
    
    # Define enhanced transforms with data augmentation for real-world conditions
    data_transforms = {
        'train': transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),  # Handle different angles
            transforms.ColorJitter(
                brightness=0.2,  # Handle poor lighting
                contrast=0.2,    # Handle contrast variations
                saturation=0.2   # Handle color variations (oil, rust)
            ),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),  # Handle positioning
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'test': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    data_dir = 'AutoMobile_Dataset'
    
    # Use validation set if available, otherwise use test
    if os.path.exists(os.path.join(data_dir, 'valid')):
        image_datasets = {
            'train': datasets.ImageFolder(os.path.join(data_dir, 'train'), data_transforms['train']),
            'test': datasets.ImageFolder(os.path.join(data_dir, 'valid'), data_transforms['test'])
        }
    else:
        image_datasets = {
            'train': datasets.ImageFolder(os.path.join(data_dir, 'train'), data_transforms['train']),
            'test': datasets.ImageFolder(os.path.join(data_dir, 'test'), data_transforms['test'])
        }
    
    dataloaders = {
        'train': DataLoader(image_datasets['train'], batch_size=32, shuffle=True, num_workers=4),
        'test': DataLoader(image_datasets['test'], batch_size=32, shuffle=False, num_workers=4)
    }
    
    dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'test']}
    class_names = image_datasets['train'].classes

    # Save class names
    with open('classes.json', 'w') as f:
        json.dump(class_names, f)

    print(f"Classes: {len(class_names)}")
    print(f"Training on {dataset_sizes['train']} images, testing on {dataset_sizes['test']} images")
    print(f"Data augmentation: Rotation, Flip, ColorJitter, Affine")
    
    # Calculate class weights for imbalanced dataset
    train_dataset = image_datasets['train']
    targets = [label for _, label in train_dataset.imgs]
    class_weights = compute_class_weight('balanced', classes=np.arange(len(class_names)), y=targets)
    class_weights_tensor = torch.FloatTensor(class_weights).to(device)
    print(f"Class weights calculated for imbalanced data handling")

    # Load pre-trained MobileNetV2
    model = models.mobilenet_v2(pretrained=True)
    
    # Freeze early layers (transfer learning)
    for param in model.features[:10].parameters():
        param.requires_grad = False

    # Modify final layer
    num_ftrs = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),  # Regularization
        nn.Linear(num_ftrs, len(class_names))
    )

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    print(f"Training on: {device}")

    # Use weighted loss for imbalanced classes
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=0.001, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50, eta_min=1e-6)

    # Training loop - increased epochs for better performance
    num_epochs = 50
    best_acc = 0.0
    train_losses = []
    test_accs = []
    
    # Early stopping parameters
    patience = 7
    patience_counter = 0
    
    print(f"\nStarting training for {num_epochs} epochs...")
    print(f"Early stopping patience: {patience} epochs")
    print("="*60)
    
    for epoch in range(num_epochs):
        print(f'\nEpoch {epoch+1}/{num_epochs}')
        print('-' * 60)

        # Each epoch has a training and testing phase
        for phase in ['train', 'test']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0
            
            # Use progress bar
            progress_bar = tqdm(dataloaders[phase], desc=f'{phase.capitalize()}')

            for inputs, labels in progress_bar:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
                
                # Gradient clipping to prevent exploding gradients
                if phase == 'train':
                    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                
                # Update progress bar
                if phase == 'train':
                    progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})

            if phase == 'train':
                scheduler.step()
            
            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]
            
            if phase == 'train':
                train_losses.append(epoch_loss)
                print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')
            else:
                test_accs.append(epoch_acc.item())
                print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')
                
                # Save best model
                if epoch_acc > best_acc:
                    best_acc = epoch_acc
                    torch.save(model.state_dict(), 'spare_part_model.pth')
                    print(f'✓ Saved best model with accuracy: {best_acc:.4f}')
                    patience_counter = 0  # Reset patience counter
                else:
                    patience_counter += 1
                    print(f'⚠ No improvement. Patience: {patience_counter}/{patience}')
        
        # Early stopping check
        if patience_counter >= patience:
            print(f"\n⏹ Early stopping triggered at epoch {epoch+1}")
            print(f"Best accuracy achieved: {best_acc:.4f}")
            break

    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f'Best Test Accuracy: {best_acc:.4f}')

    # Plot training curves
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss Curve')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(test_accs, label='Test Accuracy', color='green')
    plt.axhline(y=best_acc, color='r', linestyle='--', label=f'Best: {best_acc:.4f}')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title('Test Accuracy Curve')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('training_curves.png', dpi=150)
    print("✓ Training curves saved to training_curves.png")
    
    return model, class_names, best_acc

if __name__ == "__main__":
    train_model()
