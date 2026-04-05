import math

# ROBOT COMPONENTS
h1 = 45
h2 = 45
w1 = 45
w2 = 45
l = 45

# TOLERANCES
F_TOLERANCE = 1.0          # each F-value must be close to zero
F_RMSE_TOLERANCE = 1.0     # overall RMSE of F-values from zero
T_STD_TOLERANCE = 1.0      # T-values must be close to each other

# INPUT SENSOR RECORDS
# Internal format: [d1, d2, d3, d4, theta]
records = []

n = int(input("Enter number of sensor records: "))

for i in range(n):
    print("\nRecord", i + 1)
    d1 = float(input("Enter d1: "))
    d2 = float(input("Enter d2: "))
    d3 = float(input("Enter d3: "))
    d4 = float(input("Enter d4: "))
    theta = float(input("Enter theta (in degrees): "))

    records.append([d1, d2, d3, d4, theta])


# WHEN ROBOT IS TILTED
def compute_h_prime(theta, w1, w2):
    theta_rad = math.radians(theta)

    if theta > 0:   # tilted to the right
        h_prime = w2 * math.tan(theta_rad)
    elif theta < 0: # tilted to the left
        h_prime = w1 * math.tan(theta_rad)
    else:
        h_prime = 0

    return h_prime


# SAFE SQRT
def safe_sqrt(value):
    if value < 0:
        if abs(value) < 1e-10:
            value = 0
        else:
            return None
    return math.sqrt(value)


# T1...T10 USE THIS
# Circumradius formula from triangle sides a, b, c
def compute_triangle_radius(a, b, c):
    radicand = (a + b + c) * (-a + b + c) * (a - b + c) * (a + b - c)
    denominator = safe_sqrt(radicand)

    if denominator is None or denominator == 0:
        return None

    return (a * b * c) / denominator


# COMPONENTS OF D0, D1, D2, D3, D4
def compute_f_values(d1, d2, d3, d4, h_prime, h1, h2, w1, w2, l):
    f1 = ((w1 + d1) ** 2 + (h2 + d2) ** 2) ** 0.5
    f2 = ((w1 + d1) ** 2 + (l + d3) ** 2 - 2 * (w1 + d1) * (l + d3) * math.cos(math.radians(135))) ** 0.5
    f3 = ((h1 + h_prime) ** 2 + (w1 + d1) ** 2) ** 0.5
    f4 = ((h1 + h_prime) ** 2 + (w2 + d4) ** 2) ** 0.5
    f5 = ((w2 + d4) ** 2 + (l + d3) ** 2 - 2 * (w2 + d4) * (l + d3) * math.cos(math.radians(45))) ** 0.5
    f6 = ((h1 + h_prime) ** 2 + (l + d3) ** 2 - 2 * (h1 + h_prime) * (l + d3) * math.cos(math.radians(135))) ** 0.5
    f7 = ((w2 + d4) ** 2 + (h2 + d2) ** 2) ** 0.5
    f8 = ((l + d3) ** 2 + (h2 + d2) ** 2 - 2 * (l + d3) * (h2 + d2) * math.cos(math.radians(45))) ** 0.5
    f9 = h_prime + h1 + h2 + d2
    f10 = d1 + w1 + w2 + d4

    return [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10]


# INTERSECTING CHORD THEOREM AND PTOLEMY'S THEOREM
def compute_F_values(f, d1, d2, d4, w1, w2, h1, h_prime, h2):
    f1, f2, f3, f4, f5, f6, f7, f8, f9, f10 = f

    F1 = ((d1 + w1) * (w2 + d4)) - ((h1 + h_prime) * (h2 + d2))
    F2 = f3 * f5 + f2 * f4 - f6 * f10
    F3 = f1 * f5 + f8 * f10 - f2 * f7
    F4 = f4 * f8 + f5 * f9 - f6 * f7
    F5 = f1 * f6 + f3 * f8 - f2 * f9
    F6 = f1 * f4 + f3 * f7 - f9 * f10

    return [F1, F2, F3, F4, F5, F6]


# T1...T10 AS RADIUS ESTIMATES
def compute_T_values(f):
    f1, f2, f3, f4, f5, f6, f7, f8, f9, f10 = f

    T1 = compute_triangle_radius(f1, f3, f9)
    T2 = compute_triangle_radius(f2, f3, f6)
    T3 = compute_triangle_radius(f3, f4, f10)
    T4 = compute_triangle_radius(f6, f8, f9)
    T5 = compute_triangle_radius(f4, f7, f9)
    T6 = compute_triangle_radius(f4, f5, f6)
    T7 = compute_triangle_radius(f1, f2, f8)
    T8 = compute_triangle_radius(f1, f7, f10)
    T9 = compute_triangle_radius(f2, f5, f10)
    T10 = compute_triangle_radius(f5, f7, f8)

    return [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]


def compute_mean(values):
    return sum(values) / len(values)


def compute_stddev(values):
    mean_value = compute_mean(values)
    variance = 0

    for value in values:
        variance += (value - mean_value) ** 2

    variance = variance / len(values)   # population standard deviation
    return variance ** 0.5


# RMSE OF F-VALUES FROM ZERO
def compute_rmse_from_zero(values):
    total = 0
    for value in values:
        total += value ** 2

    mean_square = total / len(values)
    rmse = mean_square ** 0.5
    return rmse


# FINAL EVALUATION OF EACH RECORD
def evaluate_record(F_values, T_values, f_tolerance, f_rmse_tolerance, t_std_tolerance):
    # 1) Check each F-value individually
    F_close_to_zero = True
    for value in F_values:
        if abs(value) > f_tolerance:
            F_close_to_zero = False
            break

    # 2) Check RMSE of F-values from zero
    F_rmse = compute_rmse_from_zero(F_values)
    F_rmse_check = F_rmse <= f_rmse_tolerance

    # 3) Check if all T-values are valid
    T_valid = True
    for value in T_values:
        if value is None:
            T_valid = False
            break

    if T_valid:
        T_mean = compute_mean(T_values)
        T_stddev = compute_stddev(T_values)
    else:
        T_mean = None
        T_stddev = None

    # 4) Check if T-values are close to each other
    if T_stddev is not None and T_stddev <= t_std_tolerance:
        T_consistent = True
    else:
        T_consistent = False

    # 5) Final circular condition
    if F_close_to_zero and F_rmse_check and T_consistent:
        shape = "Circular"
        radius = T_mean
        area = math.pi * (radius ** 2)
    else:
        shape = "Rectangular"
        radius = None
        area = None

    return shape, radius, area, T_mean, T_stddev, F_close_to_zero, F_rmse, F_rmse_check, T_consistent


# PROCESS ALL RECORDS
f_matrix = []
F_matrix = []
T_matrix = []
shape_list = []
shape_num_list = []
radius_list = []
area_list = []
t_mean_list = []
t_stddev_list = []
F_check_list = []
F_rmse_list = []
F_rmse_check_list = []
T_check_list = []
combined_numeric = []

for record in records:
    d1, d2, d3, d4, theta = record

    h_prime = compute_h_prime(theta, w1, w2)

    # Compute f-values
    f_values = compute_f_values(d1, d2, d3, d4, h_prime, h1, h2, w1, w2, l)
    f_matrix.append(f_values)

    # Compute F-values
    F_values = compute_F_values(f_values, d1, d2, d4, w1, w2, h1, h_prime, h2)
    F_matrix.append(F_values)

    # Compute T-values
    T_values = compute_T_values(f_values)
    T_matrix.append(T_values)

    # Evaluate record
    shape, radius, area, T_mean, T_stddev, F_close_to_zero, F_rmse, F_rmse_check, T_consistent = evaluate_record(
        F_values, T_values, F_TOLERANCE, F_RMSE_TOLERANCE, T_STD_TOLERANCE
    )

    shape_list.append(shape)
    radius_list.append(radius)
    area_list.append(area)
    t_mean_list.append(T_mean)
    t_stddev_list.append(T_stddev)
    F_check_list.append(F_close_to_zero)
    F_rmse_list.append(F_rmse)
    F_rmse_check_list.append(F_rmse_check)
    T_check_list.append(T_consistent)

    if shape == "Circular":
        shape_num = 1
    else:
        shape_num = 0

    shape_num_list.append(shape_num)

    # Convert logical checks to numeric
    if F_close_to_zero:
        F_check_num = 1
    else:
        F_check_num = 0

    if F_rmse_check:
        F_rmse_check_num = 1
    else:
        F_rmse_check_num = 0

    if T_consistent:
        T_check_num = 1
    else:
        T_check_num = 0

    # Replace None in T-values with NaN for numeric analysis
    T_numeric = []
    for value in T_values:
        if value is None:
            T_numeric.append(float("nan"))
        else:
            T_numeric.append(value)

    if T_mean is None:
        T_mean_numeric = float("nan")
    else:
        T_mean_numeric = T_mean

    if T_stddev is None:
        T_stddev_numeric = float("nan")
    else:
        T_stddev_numeric = T_stddev

    if radius is None:
        radius_numeric = float("nan")
    else:
        radius_numeric = radius

    if area is None:
        area_numeric = float("nan")
    else:
        area_numeric = area

    # theta and h_prime are NOT displayed here
    combined_row = (
        [d1, d2, d3, d4]
        + f_values
        + F_values
        + T_numeric
        + [T_mean_numeric, T_stddev_numeric, F_check_num, F_rmse, F_rmse_check_num, T_check_num, radius_numeric, area_numeric, shape_num]
    )
    combined_numeric.append(combined_row)


# DISPLAY RESULTS
print("\n=== SENSOR RECORDS ===")
for i in range(len(records)):
    d1, d2, d3, d4, theta = records[i]
    print("Record", i + 1, ":", [d1, d2, d3, d4])

print("\n=== f_matrix (f1 to f10) ===")
for i in range(len(f_matrix)):
    print("Record", i + 1, ":", f_matrix[i])

print("\n=== F_matrix (F1 to F6) ===")
for i in range(len(F_matrix)):
    print("Record", i + 1, ":", F_matrix[i])

print("\n=== T_matrix (T1 to T10) ===")
for i in range(len(T_matrix)):
    print("Record", i + 1, ":", T_matrix[i])

print("\n=== STATISTICAL ANALYSIS ===")
for i in range(len(records)):
    print("Record", i + 1)
    print("  Mean of T-values     =", t_mean_list[i])
    print("  Std. Deviation of T  =", t_stddev_list[i])
    print("  F near zero check    =", F_check_list[i])
    print("  F RMSE from zero     =", F_rmse_list[i])
    print("  F RMSE check         =", F_rmse_check_list[i])
    print("  T consistency check  =", T_check_list[i])
    print("  Estimated radius     =", radius_list[i])
    print("  Circular area        =", area_list[i])

print("\n=== SHAPE PER RECORD ===")
for i in range(len(shape_list)):
    print("Record", i + 1, ":", shape_list[i])

print("\n=== COMBINED NUMERIC MATRIX ===")
for i in range(len(combined_numeric)):
    print("Record", i + 1, ":", combined_numeric[i])
