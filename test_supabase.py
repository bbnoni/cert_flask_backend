# from supabase import create_client
# import os
# from dotenv import load_dotenv

# load_dotenv()  # ✅ Load variables from .env

# url = os.getenv("SUPABASE_URL")
# key = os.getenv("SUPABASE_KEY")

# assert url and key, "❌ Missing Supabase credentials in environment"

# supabase = create_client(url, key)
# print("✅ Supabase client created successfully!")


from supabase.client import Client, create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

assert url and key, "❌ Missing Supabase credentials in environment"

supabase: Client = create_client(url, key)
print("✅ Supabase client created successfully!")
