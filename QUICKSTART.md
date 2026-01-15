# 🚀 QUICK START - No Database Setup Required!

## Instant Testing Mode

Linky V2 now includes a **bypass mode** that lets you test the app immediately without setting up Supabase!

### How to Use:

1. **Just run the app:**
   ```bash
   streamlit run app.py
   ```

2. **Use your professional access code:**
   Contact the administrator to receive your secure code.

3. **Start generating content!**

### What Works in Bypass Mode:

✅ Access code validation
✅ Content generation (all features)
✅ Metrics tracking (in-memory)
✅ Like/Share buttons
✅ Geolocation & timezone
✅ Social sharing
✅ Word count slider (50-1700)
✅ All premium LLM models

### What's Different:

⚠️ Metrics reset when you restart the app (not persistent)
⚠️ No permanent storage of posts
⚠️ Access codes can be reused

---

## Set Up Full Database Later (Optional)

When you're ready for production with persistent storage:

1. Go to Supabase SQL Editor: https://supabase.com/dashboard/project/vzhyijiilkplwurvipkz/sql/new

2. Run the `supabase_setup.sql` script

3. Restart the app - it will automatically detect the database and switch off bypass mode

---

**That's it! You can start using Linky right now! 🎉**
