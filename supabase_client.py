# import os
# from supabase import create_client

# SUPABASE_URL = "https://fhnxhnhbpjkedbuptzd.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZobnhobmJocGprZWRidWZwdHpkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODg3MjkyNiwiZXhwIjoyMDY0NDQ4OTI2fQ.RIKA8_QcegoSAN46Rt_2L565uwxM3CIF7RHKDmXBDF4"

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)




