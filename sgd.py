import numpy as np

# Example training data
X = np.array([[1, 2], [2, 3], [3, 4]])
y = np.array([3, 5, 7])

# Initialize parameters
theta = np.random.randn(2)
print(f'Parameters before Training: {theta}')
learning_rate = 0.01
num_epochs = 10000

# SGD implementation
for epoch in range(num_epochs):
    # print(f"Epoch: {epoch}")
    for i in range(len(y)):
        # Compute prediction
        y_pred = np.dot(X[i], theta)
        # Compute error
        error = y_pred - y[i]
        # Compute gradient
        gradient = X[i] * error
        # Update parameters
        theta = theta - learning_rate * gradient

print("Trained parameters:", theta)
