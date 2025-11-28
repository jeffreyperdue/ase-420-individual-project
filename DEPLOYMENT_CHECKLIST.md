# Deployment Checklist

## ✅ Pre-Deployment (Already Done)
- [x] Hugo site structure created
- [x] Content pages created (4 pages)
- [x] PDF files copied to `hugo/static/pdfs/`
- [x] GitHub Actions workflow created
- [x] Theme and templates configured

## 🚀 Deployment Steps

### Step 1: Enable GitHub Pages
- [ ] Go to: https://github.com/jeffreyperdue/ase-420-individual-project/settings/pages
- [ ] Under **Source**, select **GitHub Actions** (NOT "Deploy from a branch")
- [ ] Click **Save**

### Step 2: Commit and Push
Run these commands:
```bash
git add hugo/ .github/workflows/hugo.yml HUGO_DEPLOYMENT.md QUICK_START.md
git commit -m "Add Hugo site for GitHub Pages deployment"
git push origin main
```

### Step 3: Monitor Deployment
- [ ] Go to: https://github.com/jeffreyperdue/ase-420-individual-project/actions
- [ ] Find the "Deploy Hugo site to Pages" workflow
- [ ] Wait for it to complete (green checkmark)
- [ ] Usually takes 2-3 minutes

### Step 4: Verify Site is Live
- [ ] Visit: https://jeffreyperdue.github.io/ase-420-individual-project/
- [ ] Check that all 4 pages are accessible:
  - [ ] Home page loads
  - [ ] Final Presentation page works
  - [ ] Architecture page works
  - [ ] Project Progress page works
  - [ ] User Guide page works
- [ ] Verify PDFs are viewable/downloadable

## 🎉 Success!
Once all steps are complete, your documentation site will be live on GitHub Pages!

## 🔧 Troubleshooting

**If deployment fails:**
- Check the Actions tab for error messages
- Verify all PDF files are committed to git
- Ensure GitHub Pages is set to use "GitHub Actions" source

**If site doesn't update:**
- Wait 2-3 minutes for GitHub Pages to rebuild
- Clear browser cache (Ctrl+F5)
- Check Actions tab for deployment status

**If PDFs don't display:**
- Verify PDFs are in `hugo/static/pdfs/` and committed
- Check file paths in content markdown files match actual filenames

