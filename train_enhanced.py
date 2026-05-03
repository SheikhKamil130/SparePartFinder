import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.utils.class_weight import compute_class_weight
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from tqdm import tqdm

def train_enhanced_model():
    """Train ResNet50 model with advanced techniques for 90%+ precision and F1"""
    
    # Advanced data augmentation
    data_transforms = {
        'train': transforms.Compose([
            transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.1),
            transforms.RandomRotation(20),
            transforms.ColorJitter(
                brightness=0.3,
                contrast=0.3,
                saturation=0.3,
                hue=0.1
            ),
            transforms.RandomAffine(degrees=0, translate=(0.15, 0.15), scale=(0.85, 1.15)),
            transforms.RandomPerspective(distortion_scale=0.2, p=0.3),
            transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            transforms.RandomErasing(p=0.2, scale=(0.02, 0.15))
        ]),
        'test': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    data_dir = 'AutoMobile_Dataset'
    
    # Load datasets
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
        'train': DataLoader(image_datasets['train'], batch_size=32, shuffle=True, num_workers=4, pin_memory=True),
        'test': DataLoader(image_datasets['test'], batch_size=32, shuffle=False, num_workers=4, pin_memory=True)
    }
    
    dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'test']}
    class_names = image_datasets['train'].classes

    # Save class names
    with open('classes.json', 'w') as f:
        json.dump(class_names, f)

    print(f"Classes: {len(class_names)}")
    print(f"Training on {dataset_sizes['train']} images, testing on {dataset_sizes['test']} images")
    print(f"Model: ResNet50 with advanced augmentation")
    
    # Calculate class weights
    train_dataset = image_datasets['train']
    targets = [label for _, label in train_dataset.imgs]
    class_weights = compute_class_weight('balanced', classes=np.arange(len(class_names)), y=targets)
    class_weights_tensor = torch.FloatTensor(class_weights)
    print(f"Class weights calculated")

    # Use ResNet50 (better accuracy than MobileNetV2)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")
    
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    
    # Freeze only early layers (fine-tune more)
    for param in list(model.parameters())[:50]:
        param.requires_grad = False

    # Modify final layer
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(num_ftrs, 256),
        nn.ReLU(),
        nn.BatchNorm1d(256),
        nn.Dropout(0.3),
        nn.Linear(256, len(class_names))
    )

    model = model.to(device)

    # Weighted loss for imbalanced classes
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor.to(device))
    
    # AdamW optimizer with weight decay
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()), 
        lr=0.001, 
        weight_decay=0.01
    )
    
    # Cosine annealing with warm restarts
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, 
        T_0=10, 
        T_mult=2, 
        eta_min=1e-6
    )

    # Training loop - 100 epochs
    num_epochs = 100
    best_f1 = 0.0
    train_losses = []
    test_metrics = []
    
    # Early stopping
    patience = 15
    patience_counter = 0
    
    print(f"\nStarting training for {num_epochs} epochs...")
    print(f"Early stopping patience: {patience} epochs")
    print("="*60)
    
    for epoch in range(num_epochs):
        print(f'\nEpoch {epoch+1}/{num_epochs}')
        print('-' * 60)

        for phase in ['train', 'test']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0
            y_true = []
            y_pred = []
            
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
                        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
                y_true.extend(labels.cpu().numpy())
                y_pred.extend(preds.cpu().numpy())
                
                if phase == 'train':
                    progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})

            if phase == 'train':
                scheduler.step()
            
            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]
            
            # Calculate precision and F1
            precision, recall, f1, _ = precision_recall_fscore_support(
                y_true, y_pred, average='weighted', zero_division=0
            )
            
            if phase == 'train':
                train_losses.append(epoch_loss)
                print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')
            else:
                test_metrics.append({'acc': epoch_acc.item(), 'precision': precision, 'f1': f1})
                print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f} F1: {f1:.4f} Prec: {precision:.4f}')
                
                # Save best model based on F1 score
                if f1 > best_f1:
                    best_f1 = f1
                    best_precision = precision
                    torch.save(model.state_dict(), 'spare_part_model.pth')
                    print(f'✓ Saved best model with F1: {best_f1:.4f}, Precision: {best_precision:.4f}')
                    patience_counter = 0
                else:
                    patience_counter += 1
                    print(f'⚠ No improvement. Patience: {patience_counter}/{patience}')
        
        # Early stopping
        if patience_counter >= patience:
            print(f"\n⏹ Early stopping triggered at epoch {epoch+1}")
            print(f"Best F1 score achieved: {best_f1:.4f}")
            break

    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f'Best F1-Score: {best_f1:.4f}')
    print(f'Best Precision: {best_precision:.4f}')

    # Plot training curves
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.plot(train_losses, label='Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 3, 2)
    accs = [m['acc'] for m in test_metrics]
    plt.plot(accs, label='Test Accuracy', color='green')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title('Test Accuracy')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 3, 3)
    f1s = [m['f1'] for m in test_metrics]
    plt.plot(f1s, label='F1-Score', color='purple')
    plt.plot([m['precision'] for m in test_metrics], label='Precision', color='orange')
    plt.axhline(y=0.90, color='r', linestyle='--', label='Target: 0.90')
    plt.xlabel('Epoch')
    plt.ylabel('Score')
    plt.title('F1 & Precision')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('training_curves.png', dpi=150)
    print("✓ Training curves saved")
    
    return model, class_names, best_f1

if __name__ == "__main__":
    train_enhanced_model()
