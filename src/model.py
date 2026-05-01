import torch
import torch.nn as nn
import timm

class TrueKaratModel(nn.Module):
    def __init__(self, num_purity_classes=4, num_type_classes=10, pretrained=True):
        super(TrueKaratModel, self).__init__()
        
        # Backbone: EfficientNet-B3
        # Outputs a 1536-dim feature vector
        self.backbone = timm.create_model('efficientnet_b3', pretrained=pretrained, num_classes=0)
        
        # Feature dimension for EfficientNet-B3 is 1536
        feature_dim = 1536
        
        # 4 Task-specific heads
        # 1. Purity Head (Classifier: 14K, 18K, 22K, 24K)
        self.purity_head = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(feature_dim, num_purity_classes)
        )
        
        # 2. Weight Head (Regression: grams)
        self.weight_head = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(feature_dim, 1) # Outputs a single value for weight
        )
        
        # 3. Fraud Head (Binary Classifier: genuine vs fake)
        # We output 1 logit, BCEWithLogitsLoss will be used
        self.fraud_head = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(feature_dim, 1)
        )
        
        # 4. Type Head (Multiclass: ring, bangle, chain, etc. - 10 classes)
        self.type_head = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(feature_dim, num_type_classes)
        )

    def forward(self, x):
        # Extract features from backbone
        features = self.backbone(x)
        
        # Pass features through each head
        purity_logits = self.purity_head(features)
        weight_pred = self.weight_head(features)
        fraud_logits = self.fraud_head(features)
        type_logits = self.type_head(features)
        
        return purity_logits, weight_pred, fraud_logits, type_logits
