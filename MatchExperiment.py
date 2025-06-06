import math
import matplotlib.pyplot as plt

# Normalization and penalty function using binary entropy
def predictability_penalty(num_right, num_left):
    total = num_right + num_left
    if total <= 1:
        return 0.0
    p = num_right / total
    if p in [0, 1]:
        return 1.0
    entropy = - (p * math.log2(p) + (1 - p) * math.log2(1 - p))
    # return 1 - (entropy / 1)  # Normalize
    return 1 - math.exp(-5 * (1 - entropy))  # Closer to 1 faster

# Fitness equations
def fitness_serving_right(h1, H1, H2, y, penalty):
    return H2 * (h1 + 1 + H1 * (1 - y)) - penalty

def fitness_serving_left(h1, h2, H1, y, penalty):
    return h2 * (h1 + 1 + H1 * (1 - y)) - penalty

def fitness_returning_right(h1, x, penalty):
    return h1 * x - penalty

def fitness_returning_left(H1, x, penalty):
    return H1 * x - penalty

# Normalized potencies from match data
h1 = 0.215  # Sinner Forehand
H1 = 0.945  # Sinner Backhand
h2 = 0.74   # Griekspoor Forehand
H2 = 0.055  # Griekspoor Backhand

# Weakness (1 - normalized potency)
w_h1 = 1 - h1
w_H1 = 1 - H1
w_h2 = 1 - h2
w_H2 = 1 - H2

# Initial strategy probabilities
x = 0.35  # Return right
y = 0.49  # Serve right

# Tracking counts
num_right_serves = 0
num_left_serves = 0
num_right_returns = 0
num_left_returns = 0

# Lists for visualization
x_vals, y_vals = [], []
penalty_serve_vals, penalty_return_vals = [], []

x_vals.append(x)
y_vals.append(y)

# Simulate 145 points (average of a real match)
for t in range(145):
    # Compute penalties
    serve_penalty = predictability_penalty(num_right_serves, num_left_serves)
    return_penalty = predictability_penalty(num_right_returns, num_left_returns)

    penalize_fR = num_right_serves > num_left_serves
    penalize_FR = num_right_returns > num_left_returns

    fR = fitness_serving_right(h1, H1, w_H2, y, serve_penalty if penalize_fR else 0)
    fL = fitness_serving_left(h1, h2, w_h2, y, serve_penalty if not penalize_fR else 0)

    FR = fitness_returning_right(w_H1, x, return_penalty if penalize_FR else 0)
    FL = fitness_returning_left(w_h1, x, return_penalty if not penalize_FR else 0)

    # Replicator dynamics
    dx_dt = x * (1 - x) * (FR - FL)
    dy_dt = y * (1 - y) * (fR - fL)

    x += dx_dt
    y += dy_dt

    # Clamp x, y to [0, 1]
    x = min(max(x, 0), 1)
    y = min(max(y, 0), 1)

    import random

    # Simulate serve direction
    if random.random() < y:
        num_right_serves += 1
    else:
        num_left_serves += 1

    # Simulate return direction
    if random.random() < x:
        num_right_returns += 1
    else:
        num_left_returns += 1

    # Store results for plotting
    x_vals.append(x)
    y_vals.append(y)
    penalty_serve_vals.append(serve_penalty)
    penalty_return_vals.append(return_penalty)

    if abs(dx_dt) < 1e-4 and abs(dy_dt) < 1e-4:
      print(f"Equilibrium reached at x={x:.3f}, y={y:.3f}")


# Plotting
plt.figure(figsize=(12, 5))

# Strategy evolution
plt.subplot(1, 2, 1)
plt.plot(x_vals, label='x (Return Right)')
plt.plot(y_vals, label='y (Serve Right)')
plt.xlabel('Point')
plt.ylabel('Strategy Probability')
plt.title('Strategy Evolution')
plt.legend()

# Penalty evolution
plt.subplot(1, 2, 2)
plt.plot(penalty_serve_vals, label='Serve Penalty')
plt.plot(penalty_return_vals, label='Return Penalty')
plt.xlabel('Point')
plt.ylabel('Penalty')
plt.title('Penalty Over Time')
plt.legend()

plt.tight_layout()
plt.show()
