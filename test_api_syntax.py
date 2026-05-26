import sys
from unittest.mock import MagicMock

# Mock out external dependencies
sys.modules['supabase'] = MagicMock()
sys.modules['supabase._async'] = MagicMock()
sys.modules['supabase._async.client'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['gotrue'] = MagicMock()
sys.modules['redis'] = MagicMock()
sys.modules['redis.asyncio'] = MagicMock()

import api
print("API imported successfully!")
