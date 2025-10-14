from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

def evaluate_model_metrics(model, X_test, y_test, word_ids):
    predictions = model.predict(X_test)
    y_pred = np.argmax(predictions, axis=1)
    y_true = np.argmax(y_test, axis=1)
    
    # Matriz de confusión
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', xticklabels=word_ids, yticklabels=word_ids)
    plt.title('Matriz de Confusión')
    plt.ylabel('Real')
    plt.xlabel('Predicción')
    plt.savefig('confusion_matrix.png')
    
    # Reporte de clasificación
    print(classification_report(y_true, y_pred, target_names=word_ids))

# Llamar esto después de entrenar