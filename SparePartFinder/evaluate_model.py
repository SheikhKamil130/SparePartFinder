import torch
import torch.nn as nn
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
from sklearn.metrics import precision_recall_fscore_support, classification_report, confusion_matrix
from sklearn.metrics import accuracy_score
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def evaluate_model():
    """Comprehensive model evaluation (Aim 5 - Rigorous Evaluation)"""
    
    # Load class names
    with open('classes.json', 'r') as f:
        class_names = json.load(f)

    # Define test transforms
    test_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    data_dir = 'AutoMobile_Dataset'
    
    # Use test directory
    test_dir = os.path.join(data_dir, 'test')
    if not os.path.exists(test_dir):
        print(f"Warning: {test_dir} not found. Using validation set.")
        test_dir = os.path.join(data_dir, 'valid')
    
    test_dataset = datasets.ImageFolder(test_dir, test_transforms)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=4)

    # Load the model
    model = models.mobilenet_v2(weights=None)  # Updated: use weights=None instead of pretrained=False
    num_ftrs = model.classifier[1].in_features
    
    # Match the architecture used in training (check if it's Sequential or Linear)
    # Try Sequential first (new training format)
    try:
        model.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(num_ftrs, len(class_names))
        )
        model.load_state_dict(torch.load('spare_part_model.pth', map_location=torch.device('cpu')))
    except RuntimeError:
        # Fallback to old format (Linear only)
        model.classifier[1] = nn.Linear(num_ftrs, len(class_names))
        model.load_state_dict(torch.load('spare_part_model.pth', map_location=torch.device('cpu')))
    
    model.eval()

    y_true = []
    y_pred = []
    y_probs = []

    print("Running comprehensive evaluation on test set...")
    print("="*60)
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            y_true.extend(labels.tolist())
            y_pred.extend(preds.tolist())
            y_probs.extend(probs.max(dim=1)[0].tolist())

    # Calculate comprehensive metrics (Aim 5)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted')
    accuracy = accuracy_score(y_true, y_pred)
    
    print("\n📊 MODEL EVALUATION RESULTS")
    print("="*60)
    print(f"Overall Accuracy:     {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Weighted Precision:   {precision:.4f}")
    print(f"Weighted Recall:      {recall:.4f}")
    print(f"Weighted F1-Score:    {f1:.4f}")
    print(f"Test Samples:         {len(y_true)}")
    print(f"Number of Classes:    {len(class_names)}")
    print("="*60)
    
    print("\n📋 DETAILED CLASSIFICATION REPORT:")
    print("-"*60)
    report = classification_report(y_true, y_pred, target_names=class_names, digits=4)
    print(report)
    
    # Save report to file
    with open('evaluation_report.txt', 'w') as f:
        f.write("MODEL EVALUATION REPORT\n")
        f.write("="*60 + "\n")
        f.write(f"Accuracy: {accuracy:.4f}\n")
        f.write(f"Precision: {precision:.4f}\n")
        f.write(f"Recall: {recall:.4f}\n")
        f.write(f"F1-Score: {f1:.4f}\n\n")
        f.write("CLASSIFICATION REPORT:\n")
        f.write(report)
    print("✓ Report saved to evaluation_report.txt")
    
    # Plot confusion matrix
    print("\n📈 Generating visualizations...")
    
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(20, 15))
    sns.heatmap(cm, annot=False, cmap='Blues', fmt='d',
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix', fontsize=16, fontweight='bold')
    plt.xlabel('Predicted Label', fontsize=12)
    plt.ylabel('True Label', fontsize=12)
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=150, bbox_inches='tight')
    print("✓ Confusion matrix saved to confusion_matrix.png")
    
    # Plot accuracy distribution
    plt.figure(figsize=(10, 6))
    plt.hist(y_probs, bins=30, edgecolor='black', alpha=0.7, color='green')
    plt.title('Prediction Confidence Distribution', fontsize=14, fontweight='bold')
    plt.xlabel('Confidence Score', fontsize=12)
    plt.ylabel('Number of Predictions', fontsize=12)
    plt.axvline(x=np.mean(y_probs), color='r', linestyle='--', 
                label=f'Mean: {np.mean(y_probs):.3f}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('confidence_distribution.png', dpi=150)
    print("✓ Confidence distribution saved to confidence_distribution.png")
    
    # Print top-5 most confused classes
    print("\n🔍 TOP CONFUSIONS (Most misclassified pairs):")
    print("-"*60)
    
    # Get off-diagonal elements
    np.fill_diagonal(cm, 0)
    confused_pairs = []
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            if cm[i, j] > 0:
                confused_pairs.append((class_names[i], class_names[j], cm[i, j]))
    
    # Sort by confusion count
    confused_pairs.sort(key=lambda x: x[2], reverse=True)
    
    print("True Class -> Predicted Class (Count)")
    for true_class, pred_class, count in confused_pairs[:10]:
        print(f"{true_class:30} -> {pred_class:30} ({count})")
    
    print("\n" + "="*60)
    print("✅ EVALUATION COMPLETE!")
    print("="*60)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

if __name__ == "__main__":
    evaluate_model()
