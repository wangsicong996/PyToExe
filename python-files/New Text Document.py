def calculate_cracking_moment(b, h, d, As, n, fr, fc_prime):
    """
    Calculates the Cracking Moment (Mcr) for a reinforced concrete rectangular beam.
    """
    
    # Formula: Ytop = (b*h^2/2 + (n-1)*As*d) / (b*h + (n-1)*As)
    numerator_ytop = (b * h**2 / 2) + ((n - 1) * As * d)
    denominator_ytop = (b * h) + ((n - 1) * As)
    Ytop = numerator_ytop / denominator_ytop

    # Formula: Ybot = h - Ytop
    Ybot = h - Ytop

    # Formula: I = b*h^3/12 + b*h*(Ytop-h/2)^2 + (n-1)*As*(d-Ytop)^2
    I_concrete = (b * h**3 / 12) + (b * h * (Ytop - h / 2)**2)
    I_steel_transformed = (n - 1) * As * (d - Ytop)**2
    I = I_concrete + I_steel_transformed

    # Formula: Mcr = fr * I / Ybot * 1000
    # Factor 1000 converts MPa (kN/m^2) to achieve kN·m units.
    Mcr = (fr * 1000) * I / Ybot

    results = {
        "Ytop": Ytop,
        "Ybot": Ybot,
        "I": I,
        "Mcr_kNm": Mcr
    }

    return results

if __name__ == "__main__":
    
    print("\n--- Reinforced Concrete Cracking Moment Calculator ---")
    print("Please enter the properties for the rectangular beam.")
    
    # Input Logic
    try:
        b_val = float(input("Enter Base (b) in m: "))
        h_val = float(input("Enter Height (h) in m: "))
        d_val = float(input("Enter Effective Depth (d) in m: "))
        As_val = float(input("Enter Steel Area (As) in m^2: "))
        n_val = float(input("Enter Modular Ratio (n): "))
        fr_val = float(input("Enter Modulus of Rupture (fr) in MPa: "))
        fc_prime_val = float(input("Enter Concrete Strength (f'c) in MPa: "))
    except ValueError:
        print("\nERROR: Invalid input. Please run the program again and enter numerical values only.")
        input("Press Enter to exit...")
        exit()

    # Execution
    cracking_data = calculate_cracking_moment(
        b_val, h_val, d_val, As_val, n_val, fr_val, fc_prime_val
    )

    # Output
    print("\n--- Calculated Effective Uncracked Properties ---")
    print(f"Neutral Axis (Ytop): {'{:.4f}'.format(cracking_data['Ytop'])} m")
    print(f"Distance to Tension Face (Ybot): {'{:.4f}'.format(cracking_data['Ybot'])} m")
    print(f"Moment of Inertia (I): {'{:.6f}'.format(cracking_data['I'])} m^4")
    print("--------------------------------------------------")
    print(f"Cracking Moment (Mcr): {'{:.3f}'.format(cracking_data['Mcr_kNm'])} kN·m")
    print("--------------------------------------------------")
    
    # Prevent the console from closing immediately on Windows
    input("Calculation complete. Press Enter to exit...")