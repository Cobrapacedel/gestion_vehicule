# vehicles/utils.py

from collections import defaultdict

# Marques par type de véhicule
VEHICLE_BRANDS = {
    "car": [
        "Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "BMW", "Mercedes-Benz", "Audi",
        "Volkswagen", "Hyundai", "Kia", "Peugeot", "Renault", "Fiat", "Opel", "Tesla",
        "Porsche", "Mitsubishi", "Mazda", "Subaru", "Lexus", "Jaguar", "Land Rover", "Volvo",
        "Alfa Romeo", "Jeep", "Dacia", "Ferrari", "Lamborghini", "Bugatti",
        "Rolls-Royce", "Bentley", "McLaren"
    ],
    'moto': [
        'Yamaha', 'Suzuki', 'Kawasaki', 'Harley-Davidson', 'Ducati', 'KTM',
        'Triumph', 'Royal Enfield'
    ],
    'truck': [
        'Volvo Trucks', 'Scania', 'MAN', 'DAF', 'Iveco', 'Freightliner',
        'Mercedes-Benz Trucks', 'Kenworth'
    ],
}

# Modèles par marque
VEHICLE_MODELS = {
    # CARS
    "Toyota": ["Corolla", "Camry", "RAV4", "Highlander", "Prius", "Yaris", "Supra"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Fit", "HR-V", "Odyssey"],
    "Ford": ["Focus", "Fusion", "Escape", "Explorer", "Mustang", "F-150"],
    "Chevrolet": ["Malibu", "Impala", "Camaro", "Equinox", "Tahoe", "Silverado"],
    "Nissan": ["Altima", "Sentra", "Maxima", "Rogue", "Murano", "Pathfinder"],
    "BMW": ["Series 3", "Series 5", "Series 7", "X1", "X3", "X5", "X7"],
    "Mercedes-Benz": ["A-Class", "C-Class", "E-Class", "S-Class", "GLA", "GLC", "GLE"],
    "Audi": ["A3", "A4", "A6", "A8", "Q3", "Q5", "Q7"],
    "Volkswagen": ["Golf", "Passat", "Tiguan", "Touareg", "Jetta", "ID.4"],
    "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Palisade", "Kona"],
    "Kia": ["Rio", "Forte", "Optima", "Sportage", "Sorento", "Telluride"],
    "Peugeot": ["208", "308", "508", "2008", "3008", "5008"],
    "Renault": ["Clio", "Mégane", "Talisman", "Kadjar", "Captur", "Scénic"],
    "Fiat": ["500", "Panda", "Tipo", "Doblo", "Bravo"],
    "Opel": ["Corsa", "Astra", "Insignia", "Mokka", "Grandland X"],
    "Tesla": ["Model S", "Model 3", "Model X", "Model Y", "Cybertruck"],
    "Porsche": ["911", "Cayenne", "Macan", "Panamera", "Taycan"],
    "Mitsubishi": ["Lancer", "Outlander", "Pajero", "Eclipse Cross"],
    "Mazda": ["Mazda2", "Mazda3", "Mazda6", "CX-3", "CX-5", "MX-5"],
    "Subaru": ["Impreza", "Legacy", "Outback", "Forester", "Crosstrek"],
    "Lexus": ["IS", "ES", "GS", "LS", "NX", "RX", "UX"],
    "Jaguar": ["XE", "XF", "XJ", "F-Type", "E-PACE", "F-PACE"],
    "Land Rover": ["Range Rover", "Defender", "Discovery", "Evoque", "Velar"],
    "Volvo": ["S60", "S90", "V60", "XC40", "XC60", "XC90"],
    "Alfa Romeo": ["Giulia", "Stelvio", "Tonale", "4C"],
    "Dacia": ["Sandero", "Duster", "Lodgy", "Jogger"],
    "Jeep": ["Renegade", "Compass", "Cherokee", "Grand Cherokee", "Wrangler"],
    "Ferrari": ["F8 Tributo", "SF90 Stradale", "Roma", "296 GTB"],
    "Lamborghini": ["Huracán", "Aventador", "Urus", "Revuelto"],
    "Bugatti": ["Chiron", "Divo", "Bolide", "Mistral"],
    "Rolls-Royce": ["Phantom", "Ghost", "Wraith", "Cullinan", "Spectre"],
    "Bentley": ["Continental GT", "Flying Spur", "Bentayga"],
    "McLaren": ["570S", "720S", "Artura", "P1", "Senna"],

    # MOTOS
    "Yamaha": ["MT-07", "R1", "XSR900", "Ténéré 700"],
    "Suzuki": ["GSX-R600", "V-Strom 650", "Hayabusa"],
    "Kawasaki": ["Ninja 400", "Z900", "Versys 650"],
    "Harley-Davidson": ["Iron 883", "Street Glide", "Fat Bob"],
    "Ducati": ["Monster", "Panigale V4", "Multistrada"],
    "KTM": ["Duke 390", "RC 200", "Adventure 890"],
    "Triumph": ["Street Triple", "Tiger 900", "Bonneville"],
    "Royal Enfield": ["Classic 350", "Himalayan", "Meteor 350"],

    # TRUCKS
    "Volvo Trucks": ["FH", "FMX", "VNL"],
    "Scania": ["R-Series", "S-Series", "P-Series"],
    "MAN": ["TGX", "TGS", "TGM"],
    "DAF": ["XF", "CF", "LF"],
    "Iveco": ["Stralis", "S-Way", "Eurocargo"],
    "Freightliner": ["Cascadia", "Columbia", "M2 106"],
    "Mercedes-Benz Trucks": ["Actros", "Atego", "Econic"],
    "Kenworth": ["T680", "W900", "T880"],
}

# Fonction pour récupérer les modèles d'une marque donnée
def get_models_for_brand(brand):
    return VEHICLE_MODELS.get(brand, [])

# Validation de la cohérence : chaque marque a des modèles
def validate_vehicle_data():
    all_brands = set()
    for brand_list in VEHICLE_BRANDS.values():
        all_brands.update(brand_list)
    for brand in sorted(all_brands):
        if brand not in VEHICLE_MODELS or not VEHICLE_MODELS[brand]:
            print(f"Avertissement ⚠️ : La marque '{brand}' n'a aucun modèle associé.")

# Test manuel
if __name__ == "__main__":
    print("🚗 Modèles de Toyota :", get_models_for_brand("Toyota"))
    validate_vehicle_data()