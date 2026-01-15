import os
import database

# Mock environment if needed
# os.environ["BYPASS_DATABASE"] = "true"

print(f"BYPASS_MODE: {database.BYPASS_MODE}")
code = "LINKY2026A"
is_valid = database.validate_access_code(code)
print(f"Is '{code}' valid? {is_valid}")

user_id = "TEST_USER"
count_before = database.get_user_post_count(user_id)
print(f"Post count for {user_id} before: {count_before}")

database.save_post(user_id, "Test content", 2)
count_after = database.get_user_post_count(user_id)
print(f"Post count for {user_id} after: {count_after}")

metrics = database.get_user_metrics(user_id)
print(f"Metrics: {metrics}")
