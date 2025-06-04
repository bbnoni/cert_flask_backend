# import os
# from supabase import create_client

# SUPABASE_URL = "https://fhnxhnhbpjkedbuptzd.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZobnhobmJocGprZWRidWZwdHpkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODg3MjkyNiwiZXhwIjoyMDY0NDQ4OTI2fQ.RIKA8_QcegoSAN46Rt_2L565uwxM3CIF7RHKDmXBDF4"

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# import os
# #from supabase import create_client
# #from supabase import create_client
# from supabase_client import supabase

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# supabase = None

# if SUPABASE_URL and SUPABASE_KEY:
#     supabase = supabase(SUPABASE_URL, SUPABASE_KEY)


    
# supabase_client.py

# import os
# from dotenv import load_dotenv
# from supabase.client import Client, create_client  # ✅ use correct import for Supabase v2+

# load_dotenv()

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# assert SUPABASE_URL and SUPABASE_KEY, "❌ Missing SUPABASE_URL or SUPABASE_KEY"

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


from supabase import create_client, Client

SUPABASE_URL = "https://gottknpkjqqlmghyilcf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdvdHRrbnBranFxbG1naHlpbGNmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MzAyOTIzOSwiZXhwIjoyMDU4NjA1MjM5fQ.Fq6ya6EpS7yQFn3IbUUsh7LQIImF9soGpCv56VyPp5k"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔍 Loaded SUPABASE_URL =", SUPABASE_URL)
print("🔍 Loaded SUPABASE_KEY =", SUPABASE_KEY[:5] + "..." if SUPABASE_KEY else "❌ Missing")





