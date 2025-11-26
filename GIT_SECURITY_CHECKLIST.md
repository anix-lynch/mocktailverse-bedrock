# 🔒 Git Security Checklist

## ✅ Pre-Commit Verification

Before committing, verify:

1. **No credentials in tracked files:**
   ```bash
   grep -r "AKIA[A-Z0-9]" . --exclude-dir=.git --exclude-dir=node_modules
   # Should return no results
   ```

2. **Sensitive files are ignored:**
   ```bash
   git check-ignore AWS_AUTH.md KEY_ROTATION_COMPLETE.md SECURITY_FIX.md .cursorrules
   # Should list all files
   ```

3. **No state files:**
   ```bash
   git status | grep tfstate
   # Should return nothing
   ```

## 🚫 Files NEVER to Commit

- `AWS_AUTH.md` - Contains credentials
- `KEY_ROTATION_COMPLETE.md` - Contains credentials  
- `SECURITY_FIX.md` - Contains old credentials
- `.cursorrules` - Contains credential references
- `terraform/*.tfstate` - Terraform state
- `terraform/.terraform/` - Terraform cache
- `lambdas/*/deployment.zip` - Lambda packages
- `*.env` - Environment files
- `~/.config/secrets/global.env` - Global secrets

## ✅ Safe to Commit

- `README.md` - Public documentation
- `terraform/main.tf` - Infrastructure code
- `lambdas/*/handler.py` - Lambda source code
- `frontend/` - Next.js app (except node_modules, .next, out)
- `.gitignore` - Git ignore rules

## 🔍 Quick Check Before Push

```bash
# 1. Check for AWS keys
grep -r "AKIA[A-Z0-9]" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=venv

# 2. Check git status
git status --short

# 3. Verify ignored files
git status --ignored | grep -E "(AWS_AUTH|SECURITY|KEY_ROTATION|\.cursorrules)"
```

## ⚠️ If Credentials Found

1. **Remove from file**
2. **Add to .gitignore**
3. **Rotate keys** (if exposed)
4. **Check git history** (if already committed)

---

**Last Updated:** 2025-11-25  
**Status:** ✅ All sensitive files protected

