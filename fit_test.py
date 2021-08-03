import numpy as np
import matplotlib.pyplot as plt

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

def feature(x, order=3):
    """Generate polynomial feature of the form
    [1, x, x^2, ..., x^order] where x is the column of x-coordinates
    and 1 is the column of ones for the intercept.
    """
    x = x.reshape(-1, 1)
    return np.power(x, np.arange(order+1).reshape(1, -1)) 

I_orig = plt.imread("2Md7v.jpg")
# Convert to grayscale
I = rgb2gray(I_orig)

# Mask out region
mask = I > 20

# Get coordinates of pixels corresponding to marked region
X = np.argwhere(mask)

# Use the value as weights later
weights = I[mask] / float(I.max())
# Convert to diagonal matrix
W = np.diag(weights)

# Column indices
x = X[:, 1].reshape(-1, 1)
# Row indices to predict. Note origin is at top left corner
y = X[:, 0]


# Ridge regression, i.e., least squares with l2 regularization. 
# Should probably use a more numerically stable implementation, 
# e.g., that in Scikit-Learn
# alpha is regularization parameter. Larger alpha => less flexible curve
alpha = 0.01

# Construct data matrix, A
order = 3
A = feature(x, order)
# w = inv (A^T A + alpha * I) A^T y
w_unweighted = np.linalg.pinv( A.T.dot(A) + alpha * np.eye(A.shape[1])).dot(A.T).dot(y)
# w = inv (A^T W A + alpha * I) A^T W y
w_weighted = np.linalg.pinv( A.T.dot(W).dot(A) + alpha * \
                             np.eye(A.shape[1])).dot(A.T).dot(W).dot(y)



# Generate test points
n_samples = 50
x_test = np.linspace(0, I_orig.shape[1], n_samples)
X_test = feature(x_test, order)

# Predict y coordinates at test points
y_test_unweighted = X_test.dot(w_unweighted)
y_test_weighted = X_test.dot(w_weighted)

# Display
fig, ax = plt.subplots(1, 1, figsize=(10, 5))
ax.imshow(I_orig)
ax.plot(x_test, y_test_unweighted, color="green", marker='o', label="Unweighted")
ax.plot(x_test, y_test_weighted, color="blue", marker='x', label="Weighted")
fig.legend()
fig.savefig("curve.png")