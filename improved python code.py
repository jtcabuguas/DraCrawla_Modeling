import math

# =========================================================
# ROBOT COMPONENTS
# =========================================================
h1 = 45
h2 = 45
w1 = 45
w2 = 45
l = 45

# =========================================================
# DEFAULT TOLERANCES
# Used only if no calibration records are given
# =========================================================
DEFAULT_F_EQUIV_MARGIN = 1.0   # for TOST equivalence bound around 0
DEFAULT_F_RMSE_TOL = 1.0       # RMSE threshold for F-values
DEFAULT_K_SD_TOL = 2.0         # threshold for max z-score using SD
DEFAULT_K_MAD_TOL = 3.0        # threshold for max z-score using MAD
DEFAULT_T_CV_TOL = 0.10        # 10% coefficient of variation

# =========================================================
# BASIC HELPERS
# =========================================================
def safe_sqrt(value):
    if value < 0:
        if abs(value) < 1e-10:
            value = 0
        else:
            return None
    return math.sqrt(value)


def compute_mean(values):
    return sum(values) / len(values)


def compute_sample_variance(values):
    if len(values) < 2:
        return 0.0

    mean_value = compute_mean(values)
    total = 0.0

    for value in values:
        total += (value - mean_value) ** 2

    return total / (len(values) - 1)


def compute_sample_stddev(values):
    return compute_sample_variance(values) ** 0.5


def compute_median(values):
    sorted_values = sorted(values)
    n_values = len(sorted_values)
    mid = n_values // 2

    if n_values % 2 == 1:
        return sorted_values[mid]
    else:
        return (sorted_values[mid - 1] + sorted_values[mid]) / 2.0


def compute_mad_about_mean(values, mean_value):
    absolute_deviations = []

    for value in values:
        absolute_deviations.append(abs(value - mean_value))

    return compute_median(absolute_deviations)


def compute_max_min_difference(values):
    return max(values) - min(values)


def compute_cv(stddev_value, mean_value):
    if mean_value == 0:
        return None
    return stddev_value / abs(mean_value)


def compute_rmse_from_zero(values):
    total = 0.0
    for value in values:
        total += value ** 2

    mean_square = total / len(values)
    return mean_square ** 0.5


def compute_percentile(values, percentile):
    if len(values) == 0:
        return None

    sorted_values = sorted(values)

    if len(sorted_values) == 1:
        return sorted_values[0]

    rank = (percentile / 100.0) * (len(sorted_values) - 1)
    lower_index = int(math.floor(rank))
    upper_index = int(math.ceil(rank))

    if lower_index == upper_index:
        return sorted_values[lower_index]

    lower_value = sorted_values[lower_index]
    upper_value = sorted_values[upper_index]
    fraction = rank - lower_index

    return lower_value + (upper_value - lower_value) * fraction


# =========================================================
# T-CRITICAL VALUES
# one-sided 95% critical values for TOST (alpha = 0.05)
# two-sided 95% critical values for confidence interval
# =========================================================
ONE_SIDED_95_T = {
    1: 6.314, 2: 2.920, 3: 2.353, 4: 2.132, 5: 2.015,
    6: 1.943, 7: 1.895, 8: 1.860, 9: 1.833, 10: 1.812,
    11: 1.796, 12: 1.782, 13: 1.771, 14: 1.761, 15: 1.753,
    16: 1.746, 17: 1.740, 18: 1.734, 19: 1.729, 20: 1.725,
    21: 1.721, 22: 1.717, 23: 1.714, 24: 1.711, 25: 1.708,
    26: 1.706, 27: 1.703, 28: 1.701, 29: 1.699, 30: 1.697
}

TWO_SIDED_95_T = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
    21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
    26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042
}


def get_one_sided_95_t(df):
    if df < 1:
        return None
    if df in ONE_SIDED_95_T:
        return ONE_SIDED_95_T[df]
    return 1.645


def get_two_sided_95_t(df):
    if df < 1:
        return None
    if df in TWO_SIDED_95_T:
        return TWO_SIDED_95_T[df]
    return 1.960


# =========================================================
# GEOMETRIC FUNCTIONS
# =========================================================
def compute_h_prime(theta, w1, w2):
    theta_rad = math.radians(theta)

    if theta > 0:
        h_prime = w2 * math.tan(theta_rad)
    elif theta < 0:
        h_prime = w1 * math.tan(theta_rad)
    else:
        h_prime = 0

    return h_prime


def compute_triangle_radius(a, b, c):
    radicand = (a + b + c) * (-a + b + c) * (a - b + c) * (a + b - c)
    denominator = safe_sqrt(radicand)

    if denominator is None or denominator == 0:
        return None

    return (a * b * c) / denominator


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


def compute_F_values(f, d1, d2, d4, w1, w2, h1, h_prime, h2):
    f1, f2, f3, f4, f5, f6, f7, f8, f9, f10 = f

    F1 = ((d1 + w1) * (w2 + d4)) - ((h1 + h_prime) * (h2 + d2))
    F2 = f3 * f5 + f2 * f4 - f6 * f10
    F3 = f1 * f5 + f8 * f10 - f2 * f7
    F4 = f4 * f8 + f5 * f9 - f6 * f7
    F5 = f1 * f6 + f3 * f8 - f2 * f9
    F6 = f1 * f4 + f3 * f7 - f9 * f10

    return [F1, F2, F3, F4, F5, F6]


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


# =========================================================
# INFERENCE AND CONSISTENCY
# =========================================================
def perform_tost_against_zero(values, equivalence_margin):
    n_values = len(values)
    mean_value = compute_mean(values)

    if n_values < 2:
        return {
            "mean": mean_value,
            "sample_sd": None,
            "t_lower": None,
            "t_upper": None,
            "t_critical": None,
            "pass": abs(mean_value) < equivalence_margin
        }

    sample_sd = compute_sample_stddev(values)
    df = n_values - 1

    if sample_sd == 0:
        return {
            "mean": mean_value,
            "sample_sd": sample_sd,
            "t_lower": None,
            "t_upper": None,
            "t_critical": get_one_sided_95_t(df),
            "pass": abs(mean_value) < equivalence_margin
        }

    standard_error = sample_sd / (n_values ** 0.5)
    t_critical = get_one_sided_95_t(df)

    t_lower = (mean_value + equivalence_margin) / standard_error
    t_upper = (mean_value - equivalence_margin) / standard_error

    tost_pass = (t_lower > t_critical) and (t_upper < -t_critical)

    return {
        "mean": mean_value,
        "sample_sd": sample_sd,
        "t_lower": t_lower,
        "t_upper": t_upper,
        "t_critical": t_critical,
        "pass": tost_pass
    }


def compute_radius_confidence_interval(mean_value, sample_sd, n_values):
    if mean_value is None or sample_sd is None or n_values < 2:
        return None, None

    df = n_values - 1
    t_critical = get_two_sided_95_t(df)
    margin = t_critical * (sample_sd / (n_values ** 0.5))

    lower_bound = mean_value - margin
    upper_bound = mean_value + margin

    return lower_bound, upper_bound


def compute_T_consistency_metrics(T_values):
    valid_values = []

    for value in T_values:
        if value is None:
            return None
        valid_values.append(value)

    mean_value = compute_mean(valid_values)
    variance_value = compute_sample_variance(valid_values)
    stddev_value = compute_sample_stddev(valid_values)
    mad_value = compute_mad_about_mean(valid_values, mean_value)
    max_min_value = compute_max_min_difference(valid_values)
    cv_value = compute_cv(stddev_value, mean_value)

    if stddev_value == 0:
        max_z_sd = 0.0
    else:
        z_sd_values = []
        for value in valid_values:
            z_sd_values.append(abs(mean_value - value) / stddev_value)
        max_z_sd = max(z_sd_values)

    if mad_value == 0:
        max_z_mad = 0.0
    else:
        z_mad_values = []
        for value in valid_values:
            z_mad_values.append(abs(mean_value - value) / mad_value)
        max_z_mad = max(z_mad_values)

    sd_band = max_z_sd * stddev_value
    mad_band = max_z_mad * mad_value

    ci_lower, ci_upper = compute_radius_confidence_interval(mean_value, stddev_value, len(valid_values))

    return {
        "mean": mean_value,
        "variance": variance_value,
        "stddev": stddev_value,
        "mad": mad_value,
        "max_min": max_min_value,
        "cv": cv_value,
        "max_z_sd": max_z_sd,
        "max_z_mad": max_z_mad,
        "sd_band": sd_band,
        "mad_band": mad_band,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper
    }


# =========================================================
# RECORD METRICS
# =========================================================
def compute_record_metrics(record):
    d1, d2, d3, d4, theta = record

    h_prime = compute_h_prime(theta, w1, w2)
    f_values = compute_f_values(d1, d2, d3, d4, h_prime, h1, h2, w1, w2, l)
    F_values = compute_F_values(f_values, d1, d2, d4, w1, w2, h1, h_prime, h2)
    T_values = compute_T_values(f_values)

    F_rmse = compute_rmse_from_zero(F_values)
    T_metrics = compute_T_consistency_metrics(T_values)

    return {
        "record": record,
        "h_prime": h_prime,
        "f_values": f_values,
        "F_values": F_values,
        "T_values": T_values,
        "F_rmse": F_rmse,
        "T_metrics": T_metrics
    }


# =========================================================
# OPTIONAL CALIBRATION FOR DATA-DRIVEN TOLERANCES
# Known circular records only
# =========================================================
calibration_records = []

n_calibration = int(input("Enter number of KNOWN CIRCULAR calibration records (enter 0 if none): "))

for i in range(n_calibration):
    print("\nCalibration Record", i + 1)
    d1 = float(input("Enter d1: "))
    d2 = float(input("Enter d2: "))
    d3 = float(input("Enter d3: "))
    d4 = float(input("Enter d4: "))
    theta = float(input("Enter theta (in degrees): "))

    calibration_records.append([d1, d2, d3, d4, theta])


# =========================================================
# INPUT TEST RECORDS
# =========================================================
records = []

n = int(input("\nEnter number of sensor records to classify: "))

for i in range(n):
    print("\nTest Record", i + 1)
    d1 = float(input("Enter d1: "))
    d2 = float(input("Enter d2: "))
    d3 = float(input("Enter d3: "))
    d4 = float(input("Enter d4: "))
    theta = float(input("Enter theta (in degrees): "))

    records.append([d1, d2, d3, d4, theta])


# =========================================================
# LEARN DATA-DRIVEN TOLERANCES FROM CALIBRATION
# =========================================================
abs_F_calibration = []
F_rmse_calibration = []
max_z_sd_calibration = []
max_z_mad_calibration = []
cv_calibration = []

for calibration_record in calibration_records:
    metrics = compute_record_metrics(calibration_record)

    for value in metrics["F_values"]:
        abs_F_calibration.append(abs(value))

    F_rmse_calibration.append(metrics["F_rmse"])

    if metrics["T_metrics"] is not None:
        max_z_sd_calibration.append(metrics["T_metrics"]["max_z_sd"])
        max_z_mad_calibration.append(metrics["T_metrics"]["max_z_mad"])

        if metrics["T_metrics"]["cv"] is not None:
            cv_calibration.append(metrics["T_metrics"]["cv"])

if len(abs_F_calibration) > 0:
    F_EQUIV_MARGIN = compute_percentile(abs_F_calibration, 95)
else:
    F_EQUIV_MARGIN = DEFAULT_F_EQUIV_MARGIN

if len(F_rmse_calibration) > 0:
    F_RMSE_TOLERANCE = compute_percentile(F_rmse_calibration, 95)
else:
    F_RMSE_TOLERANCE = DEFAULT_F_RMSE_TOL

if len(max_z_sd_calibration) > 0:
    K_SD_TOLERANCE = compute_percentile(max_z_sd_calibration, 95)
else:
    K_SD_TOLERANCE = DEFAULT_K_SD_TOL

if len(max_z_mad_calibration) > 0:
    K_MAD_TOLERANCE = compute_percentile(max_z_mad_calibration, 95)
else:
    K_MAD_TOLERANCE = DEFAULT_K_MAD_TOL

if len(cv_calibration) > 0:
    T_CV_TOLERANCE = compute_percentile(cv_calibration, 95)
else:
    T_CV_TOLERANCE = DEFAULT_T_CV_TOL


# =========================================================
# EVALUATE TEST RECORDS
# =========================================================
f_matrix = []
F_matrix = []
T_matrix = []

shape_list = []
radius_list = []
area_list = []

F_rmse_list = []
F_rmse_check_list = []
F_tost_pass_list = []
F_tost_mean_list = []
F_tost_sd_list = []
F_tost_lower_list = []
F_tost_upper_list = []
F_tost_critical_list = []

T_mean_list = []
T_variance_list = []
T_stddev_list = []
T_mad_list = []
T_max_min_list = []
T_cv_list = []
T_sd_rule_list = []
T_mad_rule_list = []
T_cv_rule_list = []
k_sd_record_list = []
k_mad_record_list = []
sd_band_list = []
mad_band_list = []
ci_lower_list = []
ci_upper_list = []

for record in records:
    metrics = compute_record_metrics(record)

    f_values = metrics["f_values"]
    F_values = metrics["F_values"]
    T_values = metrics["T_values"]
    T_metrics = metrics["T_metrics"]

    f_matrix.append(f_values)
    F_matrix.append(F_values)
    T_matrix.append(T_values)

    # F analysis
    F_rmse = metrics["F_rmse"]
    F_rmse_check = F_rmse <= F_RMSE_TOLERANCE

    F_tost = perform_tost_against_zero(F_values, F_EQUIV_MARGIN)
    F_tost_pass = F_tost["pass"]

    # T analysis
    if T_metrics is not None:
        T_mean = T_metrics["mean"]
        T_variance = T_metrics["variance"]
        T_stddev = T_metrics["stddev"]
        T_mad = T_metrics["mad"]
        T_max_min = T_metrics["max_min"]
        T_cv = T_metrics["cv"]
        k_sd_record = T_metrics["max_z_sd"]
        k_mad_record = T_metrics["max_z_mad"]
        sd_band = T_metrics["sd_band"]
        mad_band = T_metrics["mad_band"]
        ci_lower = T_metrics["ci_lower"]
        ci_upper = T_metrics["ci_upper"]

        T_sd_rule = k_sd_record <= K_SD_TOLERANCE
        T_mad_rule = k_mad_record <= K_MAD_TOLERANCE

        if T_cv is not None:
            T_cv_rule = T_cv <= T_CV_TOLERANCE
        else:
            T_cv_rule = False
    else:
        T_mean = None
        T_variance = None
        T_stddev = None
        T_mad = None
        T_max_min = None
        T_cv = None
        k_sd_record = None
        k_mad_record = None
        sd_band = None
        mad_band = None
        ci_lower = None
        ci_upper = None
        T_sd_rule = False
        T_mad_rule = False
        T_cv_rule = False

    # Final decision
    if F_tost_pass and F_rmse_check and T_sd_rule and T_mad_rule and T_cv_rule:
        shape = "Circular"
        radius = T_mean
        area = math.pi * (radius ** 2)
    else:
        shape = "Rectangular"
        radius = None
        area = None

    shape_list.append(shape)
    radius_list.append(radius)
    area_list.append(area)

    F_rmse_list.append(F_rmse)
    F_rmse_check_list.append(F_rmse_check)
    F_tost_pass_list.append(F_tost_pass)
    F_tost_mean_list.append(F_tost["mean"])
    F_tost_sd_list.append(F_tost["sample_sd"])
    F_tost_lower_list.append(F_tost["t_lower"])
    F_tost_upper_list.append(F_tost["t_upper"])
    F_tost_critical_list.append(F_tost["t_critical"])

    T_mean_list.append(T_mean)
    T_variance_list.append(T_variance)
    T_stddev_list.append(T_stddev)
    T_mad_list.append(T_mad)
    T_max_min_list.append(T_max_min)
    T_cv_list.append(T_cv)
    T_sd_rule_list.append(T_sd_rule)
    T_mad_rule_list.append(T_mad_rule)
    T_cv_rule_list.append(T_cv_rule)
    k_sd_record_list.append(k_sd_record)
    k_mad_record_list.append(k_mad_record)
    sd_band_list.append(sd_band)
    mad_band_list.append(mad_band)
    ci_lower_list.append(ci_lower)
    ci_upper_list.append(ci_upper)


# =========================================================
# DISPLAY RESULTS
# =========================================================
print("\n=== LEARNED / USED TOLERANCES ===")
print("F equivalence margin for TOST =", F_EQUIV_MARGIN)
print("F RMSE tolerance             =", F_RMSE_TOLERANCE)
print("K_SD tolerance               =", K_SD_TOLERANCE)
print("K_MAD tolerance              =", K_MAD_TOLERANCE)
print("T CV tolerance               =", T_CV_TOLERANCE)

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

print("\n=== F-VALUE ANALYSIS ===")
for i in range(len(records)):
    print("Record", i + 1)
    print("  F RMSE from zero      =", F_rmse_list[i])
    print("  F RMSE check          =", F_rmse_check_list[i])
    print("  F TOST mean           =", F_tost_mean_list[i])
    print("  F TOST sample SD      =", F_tost_sd_list[i])
    print("  F TOST t_lower        =", F_tost_lower_list[i])
    print("  F TOST t_upper        =", F_tost_upper_list[i])
    print("  F TOST critical t     =", F_tost_critical_list[i])
    print("  F TOST pass           =", F_tost_pass_list[i])

print("\n=== T-VALUE ANALYSIS ===")
for i in range(len(records)):
    print("Record", i + 1)
    print("  Mean of T-values      =", T_mean_list[i])
    print("  Variance of T-values  =", T_variance_list[i])
    print("  Std. Deviation of T   =", T_stddev_list[i])
    print("  MAD of T-values       =", T_mad_list[i])
    print("  Max-Min difference    =", T_max_min_list[i])
    print("  Coefficient of Var.   =", T_cv_list[i])
    print("  Record max z (SD)     =", k_sd_record_list[i])
    print("  Record max z (MAD)    =", k_mad_record_list[i])
    print("  k*SD band             =", sd_band_list[i])
    print("  k*MAD band            =", mad_band_list[i])
    print("  SD-rule pass          =", T_sd_rule_list[i])
    print("  MAD-rule pass         =", T_mad_rule_list[i])
    print("  CV-rule pass          =", T_cv_rule_list[i])
    print("  Radius 95% CI         = [", ci_lower_list[i], ", ", ci_upper_list[i], "]", sep="")

print("\n=== FINAL RESULTS ===")
for i in range(len(records)):
    print("Record", i + 1)
    print("  Shape                 =", shape_list[i])
    print("  Estimated radius      =", radius_list[i])
    print("  Circular area         =", area_list[i])