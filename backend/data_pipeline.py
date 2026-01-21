import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List

class DataPipeline:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.demographic_datasets = []
        self.enrollment_datasets = []
        self.demographic_combined = None
        self.enrollment_combined = None
        self.master_data = None
        
    def _clean_state_name(self, state_name: str) -> str:
        """Standardize state names - ENHANCED VERSION"""
        if pd.isna(state_name):
            return "Unknown"
        
        state_name = str(state_name).strip()
        
        # Remove extra spaces
        state_name = ' '.join(state_name.split())
        
        # Map city names to their states
        city_to_state = {
            'JAIPUR': 'Rajasthan',
            'NAGPUR': 'Maharashtra',
            'DARBHANGA': 'Bihar',
            'MADANAPALLE': 'Andhra Pradesh',
            'PUTTENAHALLI': 'Karnataka',
            'RAJA ANNAMALAI PURAM': 'Tamil Nadu',
            '100000': 'Unknown'  # Invalid entry
        }
        
        # Check if it's a city name that should be a state
        state_upper = state_name.upper()
        if state_upper in city_to_state:
            return city_to_state[state_upper]
        
        # State name mappings
        mappings = {
            # West Bengal variations
            'WEST BENGAL': 'West Bengal',
            'WESTBENGAL': 'West Bengal',
            'Westbengal': 'West Bengal',
            'West bengal': 'West Bengal',
            'West Bangal': 'West Bengal',
            'West Bengli': 'West Bengal',
            'west bengal': 'West Bengal',
            'West  Bengal': 'West Bengal',
            
            # Odisha variations
            'ODISHA': 'Odisha',
            'odisha': 'Odisha',
            'Orissa': 'Odisha',
            
            # Chhattisgarh variations
            'Chatisgarh': 'Chhattisgarh',
            'Chhattisgarhh': 'Chhattisgarh',
            'CHHATTISGARH': 'Chhattisgarh',
            
            # Union Territories
            'The Dadra And Nagar Haveli And Daman And Diu': 'Dadra and Nagar Haveli and Daman and Diu',
            'Dadra & Nagar Haveli': 'Dadra and Nagar Haveli and Daman and Diu',
            'Daman & Diu': 'Dadra and Nagar Haveli and Daman and Diu',
            'Dadra and Nagar Haveli': 'Dadra and Nagar Haveli and Daman and Diu',
            'Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
            'Jammu & Kashmir': 'Jammu and Kashmir',
            'Jammu And Kashmir': 'Jammu and Kashmir',
            'Andaman & Nicobar Islands': 'Andaman and Nicobar Islands',
            'Uttaranchal': 'Uttarakhand',
            'Pondicherry': 'Puducherry'
        }
        
        # Apply mappings
        cleaned = mappings.get(state_name, state_name)
        
        # Capitalize properly if needed
        if cleaned.islower():
            cleaned = cleaned.title()
        
        return cleaned
    
    # Replace the _clean_district_name method in data_pipeline.py with this enhanced version:

    def _clean_district_name(self, district_name: str) -> str:
        
        if pd.isna(district_name):
            return "Unknown"
        
        district_name = str(district_name).strip()
        
        # Remove asterisks, extra spaces, and normalize
        district_name = district_name.replace('*', '').strip()
        district_name = ' '.join(district_name.split())
        
        # Comprehensive district mappings (add more as you discover them)
        mappings = {
        # Andhra Pradesh
        'K.v. Rangareddy': 'K.V.Rangareddy',
        'Mahabub Nagar': 'Mahbubnagar',
        'Mahabubnagar': 'Mahbubnagar',
        'Karim Nagar': 'Karimnagar',
        'Ananthapur': 'Anantapur',
        'Ananthapuramu': 'Anantapur',
        'Anantpur': 'Anantapur',
        
        # Arunachal Pradesh (East/West are different districts - keep separate)
        # West Kameng, East Kameng, West Siang, East Siang are DIFFERENT districts
        
        # Assam
        'West Karbi Anglong': 'Karbi Anglong',
        'Baska': 'Baksa',
        'Kamrup Metro': 'Kamrup Metropolitan',
        
        # Bihar
        'Samastipur': 'Samstipur',
        'Sheikhpura': 'Sheikpura',
        'West Champaran': 'Pashchim Champaran',
        'East Champaran': 'Purvi Champaran',
        'Purba Champaran': 'Purvi Champaran',
        'Pashchim Chamaparan': 'Pashchim Champaran',
        'Purvi Chamaparan': 'Purvi Champaran',
        'Aurangabad(BH)': 'Aurangabad',
        'Aurangabad(bh)': 'Aurangabad',
        'Purnia': 'Purnea',
        'Purniya': 'Purnea',
        'Muzafarpur': 'Muzaffarpur',
        'Muzzafarpur': 'Muzaffarpur',
        'Araria': 'Araria',
        'Araira': 'Araria',
        
        # Chhattisgarh
        'Janjgir - Champa': 'Janjgir-Champa',
        'Janjgir Champa': 'Janjgir-Champa',
        'Janjgir-champa': 'Janjgir-Champa',
        'Mohalla-Manpur-Ambagarh Chowki': 'Mohla-Manpur-Ambagarh Chouki',
        
        # Delhi (All are separate districts - keep as is)
        # North West Delhi, North East Delhi, etc. are DIFFERENT districts
        
        # Goa (North and South Goa are different - keep separate)
        
        # Gujarat
        'Surendra Nagar': 'Surendranagar',
        'Banas Kantha': 'Banaskantha',
        'Panch Mahals': 'Panchmahal',
        'Panchmahals': 'Panchmahal',
        'Sabar Kantha': 'Sabarkantha',
        'Ahmedabad': 'Ahmedabad',
        'Ahmadabad': 'Ahmedabad',
        'Kachchh': 'Kutch',
        'Mahesana': 'Mehsana',
        
        # Haryana
        'Yamuna Nagar': 'Yamunanagar',
        'Gurgaon': 'Gurugram',
        
        # Himachal Pradesh
        'Lahaul and Spiti': 'Lahul and Spiti',
        'Lahul & Spiti': 'Lahul and Spiti',
        
        # Jammu and Kashmir
        'Budgam': 'Badgam',
        'Bandipore': 'Bandipur',
        
        # Jharkhand
        'Hazaribagh': 'Hazaribag',
        'Palamau': 'Palamu',
        'Pakaur': 'Pakur',
        'Sahibganj': 'Sahebganj',
        'Garhwa *': 'Garhwa',
        'Koderma': 'Kodarma',
        'Pashchimi Singhbhum': 'West Singhbhum',
        'Purbi Singhbhum': 'East Singhbhum',
        'Seraikela Kharsawan': 'Seraikela-Kharsawan',
        
        # Karnataka
        'Chamarajanagar': 'Chamarajanagar',
        'Chamrajanagar': 'Chamarajanagar',
        'Chamrajnagar': 'Chamarajanagar',
        'Chamarajanagar *': 'Chamarajanagar',
        'Chickmagalur': 'Chikkamagaluru',
        'Chikmagalur': 'Chikkamagaluru',
        'Chikkamagaluru': 'Chikkamagaluru',
        'Davanagere': 'Davangere',
        'Hassan': 'Hassan',
        'Hasan': 'Hassan',
        'Bagalkot *': 'Bagalkot',
        'Haveri *': 'Haveri',
        'Tumakuru': 'Tumakuru',
        'Tumkur': 'Tumakuru',
        'Gadag *': 'Gadag',
        'Udupi *': 'Udupi',
        'Shivamogga': 'Shivamogga',
        'Shimoga': 'Shivamogga',
        'Bengaluru Rural': 'Bengaluru Rural',
        'Bangalore Rural': 'Bengaluru Rural',
        'Bangalore': 'Bengaluru Urban',
        'Bengaluru': 'Bengaluru Urban',
        'Bangalore Urban': 'Bengaluru Urban',
        'Belgaum': 'Belagavi',
        'Mysore': 'Mysuru',
        
        # Kerala
        'Kasaragod': 'Kasaragod',
        'Kasargod': 'Kasaragod',
        'Trivandrum': 'Thiruvananthapuram',
        'Alleppey': 'Alappuzha',
        'Calicut': 'Kozhikode',
        'Trichur': 'Thrissur',
        
        # Madhya Pradesh
        'Harda *': 'Harda',
        'Narsinghpur': 'Narsimhapur',
        'Hoshangabad': 'Narmadapuram',
        
        # Maharashtra
        'Chhatrapati Sambhajinagar': 'Aurangabad',
        'Chatrapati Sambhaji Nagar': 'Aurangabad',
        'Buldhana': 'Buldana',
        'Gondiya': 'Gondia',
        'Gondiya *': 'Gondia',
        'Nandurbar *': 'Nandurbar',
        'Mumbai( Sub Urban )': 'Mumbai Suburban',
        'Hingoli *': 'Hingoli',
        'Ahmed Nagar': 'Ahmednagar',
        'Ahmadnagar': 'Ahmednagar',
        'Ahilyanagar': 'Ahmednagar',
        'Washim *': 'Washim',
        'Raigarh(MH)': 'Raigad',
        'Raigarh': 'Raigad',
        'Bid': 'Beed',
        'Dharashiv': 'Osmanabad',
        'Dist : Thane': 'Thane',
        'Mumbai City': 'Mumbai',
        
        # Manipur (Imphal East and West are different - keep separate)
        
        # Meghalaya (All cardinal direction districts are separate - keep as is)
        
        # Mizoram
        'Mammit': 'Mamit',
        
        # Odisha
        'Jagatsinghapur': 'Jagatsinghpur',
        'Baleshwar': 'Balasore',
        'Baleswar': 'Balasore',
        'Jajapur': 'Jajpur',
        'JAJPUR': 'Jajpur',
        'jajpur': 'Jajpur',
        'Jajapur  *': 'Jajpur',
        'Khordha': 'Khordha',
        'Khorda': 'Khordha',
        'Khurda': 'Khordha',
        'ANUGUL': 'Angul',
        'Anugul': 'Angul',
        'Anugal': 'Angul',
        'Sundergarh': 'Sundargarh',
        'Bhadrak(R)': 'Bhadrak',
        'Debagarh': 'Deogarh',
        'Boudh': 'Baudh',
        'Cuttack': 'Cuttack',
        'Katack': 'Cuttack',
        
        # Orissa (old name for Odisha - same mappings apply)
        
        # Puducherry
        'Pondicherry': 'Puducherry',
        
        # Punjab
        'S.A.S Nagar(Mohali)': 'SAS Nagar (Mohali)',
        'Ferozepur': 'Firozpur',
        
        # Rajasthan
        'Jhunjhunun': 'Jhunjhunu',
        'Jalore': 'Jalore',
        'Jalor': 'Jalore',
        'Chittaurgarh': 'Chittorgarh',
        'Dhaulpur': 'Dholpur',
        
        # Sikkim (All cardinal direction districts are separate - keep as is)
        
        # Tamil Nadu
        'Thiruvallur': 'Tiruvallur',
        'Thiruvarur': 'Tiruvarur',
        'Kanniyakumari': 'Kanyakumari',
        'Tirupattur': 'Tirupathur',
        'Viluppuram': 'Viluppuram',
        'Villupuram': 'Viluppuram',
        'Kancheepuram': 'Kanchipuram',
        'Tiruchirapalli': 'Tiruchirappalli',
        'Trichy': 'Tiruchirappalli',
        'Tuticorin': 'Thoothukudi',
        'The Nilgiris': 'Nilgiris',
        
        # Telangana
        'Medchal?malkajgiri': 'Medchal-Malkajgiri',
        'Medchal−malkajgiri': 'Medchal-Malkajgiri',
        'Medchalâmalkajgiri': 'Medchal-Malkajgiri',
        'Medchal-malkajgiri': 'Medchal-Malkajgiri',
        'Medchal Malkajgiri': 'Medchal-Malkajgiri',
        'Warangal (urban)': 'Warangal Urban',
        'Sangareddy': 'Sangareddy',
        'Rangareddy': 'Ranga Reddy',
        'Ranga Reddy': 'Ranga Reddy',
        'K.v. Rangareddy': 'Ranga Reddy',
        'Jangoan': 'Jangaon',
        'Vishakhapatnam': 'Visakhapatnam',
        'Vizag': 'Visakhapatnam',
        'YSR': 'YSR Kadapa',
        'Cuddapah': 'YSR Kadapa',
        'Kadapa': 'YSR Kadapa',
        
        # Tripura
        'Dhalai  *': 'Dhalai',
        
        # Uttar Pradesh
        'Bulandshahar': 'Bulandshahr',
        'Maharajganj': 'Mahrajganj',
        'Jyotiba Phule Nagar *': 'Jyotiba Phule Nagar',
        'Bara Banki': 'Barabanki',
        'Rae Bareli': 'Raebareli',
        'Baghpat': 'Baghpat',
        'Bagpat': 'Baghpat',
        'Baghpat *': 'Baghpat',
        'Chitrakoot *': 'Chitrakoot',
        'Kushinagar *': 'Kushinagar',
        'Chandauli *': 'Chandauli',
        'Sant Ravidas Nagar Bhadohi': 'Sant Ravidas Nagar',
        'Gautam Buddha Nagar': 'Gautam Budh Nagar',
        'GB Nagar': 'Gautam Budh Nagar',
        'Noida': 'Gautam Budh Nagar',
        'Kanpur Nagar': 'Kanpur',
        'Kanpur Dehat': 'Kanpur Dehat',
        'Kanpur Rural': 'Kanpur Dehat',
        'Sant Kabir Nagar': 'Sant Kabir Nagar',
        'Sant Ravi Das Nagar': 'Sant Ravidas Nagar',
        'Mahamaya Nagar': 'Hathras',
        'Lakhimpur Kheri': 'Lakhimpur Kheri',
        'Kheri': 'Lakhimpur Kheri',
        'Pilibhit': 'Pilibhit',
        
        # Uttarakhand
        'Haridwar': 'Haridwar',
        'Hardwar': 'Haridwar',
        
        # West Bengal - CRITICAL FIXES FOR YOUR AREA
        'Hawrah': 'Howrah',
        'HOWRAH': 'Howrah',
        'Haora': 'Howrah',
        'Hugli': 'Hooghly',
        'Hoogly': 'Hooghly',
        'Hooghiy': 'Hooghly',
        'HOOGHLY': 'Hooghly',
        'hooghly': 'Hooghly',
        'Purba Medinipur': 'Purba Midnapore',
        'Purba Midnapur': 'Purba Midnapore',
        'East Midnapore': 'Purba Midnapore',
        'east midnapore': 'Purba Midnapore',
        'East Midnapur': 'Purba Midnapore',
        'Paschim Medinipur': 'Paschim Midnapore',
        'Paschim Midnapur': 'Paschim Midnapore',
        'West Midnapore': 'Paschim Midnapore',
        'West Medinipur': 'Paschim Midnapore',
        'Medinipur': 'Paschim Midnapore',  # Assume West if not specified
        'North 24 Parganas': 'North Twenty Four Parganas',
        'South 24 Parganas': 'South Twenty Four Parganas',
        'South 24 parganas': 'South Twenty Four Parganas',
        'South 24 Pargana': 'South Twenty Four Parganas',
        'South 24 pargana': 'South Twenty Four Parganas',
        'South  Twenty Four Parganas': 'South Twenty Four Parganas',
        'Darjiling': 'Darjeeling',
        'Darjeeling': 'Darjeeling',
        'Dakshin Dinajpur': 'Dakshin Dinajpur',
        'South Dinajpur': 'Dakshin Dinajpur',
        'Uttar Dinajpur': 'Uttar Dinajpur',
        'North Dinajpur': 'Uttar Dinajpur',
        'Koch Bihar': 'Cooch Behar',
        'Kochbihar': 'Cooch Behar',
        'Puruliya': 'Purulia',
        'Barddhaman': 'Bardhaman',
        'Paschim Bardhaman': 'Paschim Bardhaman',
        'Purba Bardhaman': 'Purba Bardhaman',
    }

        
        # Try exact match (case-insensitive)
        for key, value in mappings.items():
            if district_name.lower() == key.lower():
                return value
        
        # If no match found, ensure proper capitalization
        if district_name.islower() or district_name.isupper():
            district_name = district_name.title()
        
        return district_name
    
        
    def load_all_datasets(self):
        print("Loading demographic datasets...")
        for i in range(1, 6):
            filename = f"DEMOGRAPHIC_{i}.csv"
            filepath = self.data_dir / filename
            df = pd.read_csv(filepath)
            df['date'] = pd.to_datetime(df['date'], dayfirst=True)
            
            # Clean state and district names
            df['state'] = df['state'].apply(self._clean_state_name)
            df['district'] = df['district'].apply(self._clean_district_name)
            
            self.demographic_datasets.append(df)
            print(f"  Loaded {filename}: {len(df)} rows")
        
        print("\nLoading enrollment datasets...")
        for i in range(1, 4):
            filename = f"ENROLLMENT_{i}.csv"
            filepath = self.data_dir / filename
            df = pd.read_csv(filepath)
            df['date'] = pd.to_datetime(df['date'], dayfirst=True)
            
            # Clean state and district names
            df['state'] = df['state'].apply(self._clean_state_name)
            df['district'] = df['district'].apply(self._clean_district_name)
            
            self.enrollment_datasets.append(df)
            print(f"  Loaded {filename}: {len(df)} rows")
        
        print("\nAll datasets loaded successfully.")
    
    def merge_datasets(self):
        print("\nMerging demographic datasets...")
        self.demographic_combined = pd.concat(self.demographic_datasets, ignore_index=True)
        print(f"  Combined demographic records: {len(self.demographic_combined)}")
        
        print("\nMerging enrollment datasets...")
        self.enrollment_combined = pd.concat(self.enrollment_datasets, ignore_index=True)
        print(f"  Combined enrollment records: {len(self.enrollment_combined)}")
        
        print("\nCreating master analytical dataset...")
        self._create_master_dataset()
        print(f"  Master dataset created: {len(self.master_data)} records")
    
    def _create_master_dataset(self):
        """
        FIXED: Proper aggregation at district-date level
        - Population should be summed across pincodes (not max)
        - Enrollments should be summed across pincodes (not duplicated)
        - Filter out invalid records
        """
        
        # Remove records with invalid state names
        print("\n  Cleaning invalid state entries...")
        before_clean = len(self.demographic_combined)
        self.demographic_combined = self.demographic_combined[
            self.demographic_combined['state'] != 'Unknown'
        ]
        after_clean = len(self.demographic_combined)
        if before_clean > after_clean:
            print(f"    Removed {before_clean - after_clean} records with invalid states")
        
        before_clean = len(self.enrollment_combined)
        self.enrollment_combined = self.enrollment_combined[
            self.enrollment_combined['state'] != 'Unknown'
        ]
        after_clean = len(self.enrollment_combined)
        if before_clean > after_clean:
            print(f"    Removed {before_clean - after_clean} enrollment records with invalid states")
        
        # Aggregate demographics at district-date level (sum across pincodes)
        demo_agg = self.demographic_combined.groupby(['state', 'district', 'date']).agg({
            'demo_age_5_17': 'sum',
            'demo_age_17_': 'sum'
        }).reset_index()
        
        demo_agg['total_population'] = demo_agg['demo_age_5_17'] + demo_agg['demo_age_17_']
        
        # Remove records with zero population
        demo_agg = demo_agg[demo_agg['total_population'] > 0]
        
        # Aggregate enrollments at district-date level (sum across pincodes)
        enroll_agg = self.enrollment_combined.groupby(['state', 'district', 'date']).agg({
            'age_0_5': 'sum',
            'age_5_17': 'sum',
            'age_18_greater': 'sum'
        }).reset_index()
        
        enroll_agg['total_enrollments'] = enroll_agg['age_0_5'] + enroll_agg['age_5_17'] + enroll_agg['age_18_greater']
        
        # Merge on district-date (removed pincode from merge keys)
        self.master_data = pd.merge(
            demo_agg,
            enroll_agg,
            on=['state', 'district', 'date'],
            how='inner'  # Changed from 'outer' to 'inner' to only keep matching records
        )
        
        # Remove any remaining NaN values
        self.master_data.fillna(0, inplace=True)
        
        # Calculate penetration rates
        self.master_data['penetration_rate'] = np.where(
            self.master_data['total_population'] > 0,
            self.master_data['total_enrollments'] / self.master_data['total_population'],
            0
        )
        
        # Cap penetration rate at 100% (1.0)
        self.master_data['penetration_rate'] = self.master_data['penetration_rate'].clip(upper=1.0)
        
        self.master_data['youth_enrollment_rate'] = np.where(
            self.master_data['demo_age_5_17'] > 0,
            self.master_data['age_5_17'] / self.master_data['demo_age_5_17'],
            0
        )
        
        # Cap youth enrollment rate at 100%
        self.master_data['youth_enrollment_rate'] = self.master_data['youth_enrollment_rate'].clip(upper=1.0)
        
        self.master_data['adult_enrollment_rate'] = np.where(
            self.master_data['demo_age_17_'] > 0,
            self.master_data['age_18_greater'] / self.master_data['demo_age_17_'],
            0
        )
        
        # Cap adult enrollment rate at 100%
        self.master_data['adult_enrollment_rate'] = self.master_data['adult_enrollment_rate'].clip(upper=1.0)
        
        print(f"\n  Data quality check:")
        print(f"  - Unique states: {self.master_data['state'].nunique()}")
        print(f"  - Unique districts: {self.master_data['district'].nunique()}")
        print(f"  - Date range: {self.master_data['date'].min()} to {self.master_data['date'].max()}")
        print(f"  - Max penetration rate: {self.master_data['penetration_rate'].max():.2%}")
        print(f"  - Avg penetration rate: {self.master_data['penetration_rate'].mean():.2%}")
        print(f"  - Total population: {self.master_data['total_population'].sum():,.0f}")
        print(f"  - Total enrollments: {self.master_data['total_enrollments'].sum():,.0f}")
    
    def get_master_data(self) -> pd.DataFrame:
        return self.master_data
    
    def get_demographic_data(self) -> pd.DataFrame:
        return self.demographic_combined
    
    def get_enrollment_data(self) -> pd.DataFrame:
        return self.enrollment_combined