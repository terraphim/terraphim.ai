# Cloudflare Pages Migration Guide

**Project:** Terraphim AI
**Date:** 2025-11-13
**From:** Netlify
**To:** Cloudflare Pages

---

## Table of Contents

1. [Overview](#overview)
2. [Why Cloudflare Pages?](#why-cloudflare-pages)
3. [Pre-Migration Checklist](#pre-migration-checklist)
4. [Step-by-Step Migration](#step-by-step-migration)
5. [Configuration Files](#configuration-files)
6. [DNS Setup](#dns-setup)
7. [Post-Migration Testing](#post-migration-testing)
8. [Rollback Plan](#rollback-plan)
9. [Differences from Netlify](#differences-from-netlify)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides step-by-step instructions for migrating the Terraphim AI website from Netlify to Cloudflare Pages.

**Current Setup:**
- Hosting: Netlify
- Static Site Generator: Zola 0.14.1
- Build Command: `zola build`
- Output Directory: `public`
- Repository: https://github.com/terraphim/terraphim.ai

**Target Setup:**
- Hosting: Cloudflare Pages
- Same build configuration
- Enhanced CDN and security features
- Better performance and DDoS protection

---

## Why Cloudflare Pages?

### Benefits of Cloudflare Pages

1. **Global CDN Performance**
   - 300+ data centers worldwide
   - Faster content delivery globally
   - Automatic image optimization

2. **Enhanced Security**
   - Built-in DDoS protection
   - Web Application Firewall (WAF)
   - Free SSL certificates
   - Advanced bot protection

3. **Cost-Effective**
   - Unlimited bandwidth
   - Unlimited requests
   - Free tier is very generous
   - No hidden costs

4. **Developer Experience**
   - Instant preview deployments
   - Git integration (GitHub, GitLab)
   - Easy rollbacks
   - Build logs and analytics

5. **Integration with Cloudflare Ecosystem**
   - Cloudflare Workers for serverless functions
   - Cloudflare R2 for object storage
   - Analytics and monitoring
   - Easy DNS management

6. **Performance Features**
   - HTTP/3 and QUIC support
   - Automatic minification
   - Brotli compression
   - Smart caching

---

## Pre-Migration Checklist

Before starting the migration, ensure you have:

- [ ] Access to Cloudflare account (or create one at https://dash.cloudflare.com/sign-up)
- [ ] Access to GitHub repository (https://github.com/terraphim/terraphim.ai)
- [ ] Access to domain DNS settings (terraphim.ai)
- [ ] Backup of current Netlify configuration
- [ ] List of environment variables (if any)
- [ ] List of custom headers and redirects
- [ ] Current SSL certificate information
- [ ] Stakeholder approval for migration

### Current Environment Variables

From `netlify.toml`:
```toml
ZOLA_VERSION = "0.14.1"
```

### Current Features Used

- ✅ Static site hosting
- ✅ Automatic builds from Git
- ✅ Deploy previews
- ✅ Custom domain (terraphim.ai)
- ❌ Serverless functions (not used)
- ❌ Form handling (not used)
- ❌ Identity/Authentication (not used)

---

## Step-by-Step Migration

### Phase 1: Setup Cloudflare Pages (No Downtime)

#### Step 1: Create Cloudflare Account

1. Go to https://dash.cloudflare.com/sign-up
2. Sign up with your email
3. Verify your email address
4. Complete account setup

#### Step 2: Connect GitHub Repository

1. Navigate to **Workers & Pages** in Cloudflare dashboard
2. Click **Create application**
3. Select **Pages** tab
4. Click **Connect to Git**
5. Authorize Cloudflare Pages to access your GitHub account
6. Select the repository: `terraphim/terraphim.ai`
7. Click **Begin setup**

#### Step 3: Configure Build Settings

In the build configuration screen, set:

**Project Name:** `terraphim-ai` (or your preferred subdomain)

**Production Branch:** `main` (or your default branch)

**Build Configuration:**
```
Framework preset: None (or select "Zola" if available)
Build command: zola build
Build output directory: public
Root directory: /
```

**Environment Variables:**
```
ZOLA_VERSION = 0.14.1
```

Click **Add variable** and enter:
- Variable name: `ZOLA_VERSION`
- Value: `0.14.1`

#### Step 4: Deploy Initial Build

1. Click **Save and Deploy**
2. Wait for the build to complete (first build may take 2-3 minutes)
3. Monitor build logs for any errors
4. Once complete, you'll get a Cloudflare Pages URL like:
   - `https://terraphim-ai.pages.dev`
   - Or `https://<random-subdomain>.pages.dev`

#### Step 5: Test Cloudflare Deployment

1. Visit your Cloudflare Pages URL
2. Test all pages and functionality:
   - [ ] Homepage loads correctly
   - [ ] Navigation works
   - [ ] Dark mode toggle functions
   - [ ] Search functionality works
   - [ ] All CSS and JS files load
   - [ ] Images display correctly
   - [ ] RSS feed is accessible
   - [ ] 404 page works
3. Check browser console for any errors
4. Test on mobile devices

### Phase 2: Configure Custom Domain

#### Step 6: Add Custom Domain to Cloudflare Pages

**Option A: Domain already on Cloudflare (Recommended)**

If `terraphim.ai` is already using Cloudflare for DNS:

1. In your Cloudflare Pages project, go to **Custom domains**
2. Click **Set up a custom domain**
3. Enter `terraphim.ai`
4. Click **Continue**
5. Cloudflare will automatically create the necessary DNS records
6. Click **Activate domain**

**Option B: Domain not on Cloudflare**

1. First, add your domain to Cloudflare:
   - Go to **Websites** in Cloudflare dashboard
   - Click **Add a site**
   - Enter `terraphim.ai`
   - Follow the wizard to add your domain
   - Update your domain's nameservers at your registrar to:
     ```
     adam.ns.cloudflare.com
     ella.ns.cloudflare.com
     (or the specific nameservers Cloudflare provides)
     ```
2. Wait for nameserver propagation (can take 24-48 hours)
3. Once active, follow Option A above

#### Step 7: Add www Subdomain (Optional)

1. In **Custom domains**, click **Set up a custom domain**
2. Enter `www.terraphim.ai`
3. Click **Continue** and **Activate domain**
4. Set up a redirect from www to apex domain:
   - Go to **Rules** > **Page Rules** (or use Bulk Redirects)
   - Create redirect: `www.terraphim.ai/*` → `https://terraphim.ai/$1` (301)

### Phase 3: Configure Headers and Security

#### Step 8: Verify Custom Headers

The custom headers are configured in the `_headers` file at the project root. Cloudflare Pages will automatically use this file.

**Verify headers are applied:**

1. Visit your site
2. Open browser DevTools (F12)
3. Go to Network tab
4. Refresh the page
5. Click on the main document request
6. Check Response Headers for:
   - `X-Frame-Options: SAMEORIGIN`
   - `X-Content-Type-Options: nosniff`
   - `Content-Security-Policy: ...`
   - `Cache-Control: ...` (on static assets)

#### Step 9: Configure Additional Security Settings

1. In Cloudflare dashboard, go to **Security** > **Settings**
2. Enable recommended settings:
   - [ ] Security Level: Medium or High
   - [ ] Challenge Passage: 30 minutes
   - [ ] Browser Integrity Check: On
   - [ ] Privacy Pass: On

3. Go to **Security** > **WAF**
   - [ ] Enable managed rulesets
   - [ ] Configure any custom rules if needed

4. Go to **SSL/TLS** > **Overview**
   - [ ] Set encryption mode to **Full (strict)**

5. Go to **SSL/TLS** > **Edge Certificates**
   - [ ] Enable **Always Use HTTPS**
   - [ ] Enable **HTTP Strict Transport Security (HSTS)**
   - [ ] Enable **Automatic HTTPS Rewrites**
   - [ ] Enable **Minimum TLS Version: 1.2**

### Phase 4: Configure Performance Settings

#### Step 10: Optimize Performance

1. Go to **Speed** > **Optimization**
2. Enable:
   - [ ] Auto Minify: JavaScript, CSS, HTML
   - [ ] Brotli compression
   - [ ] HTTP/2 to Origin
   - [ ] HTTP/3 (with QUIC)
   - [ ] Early Hints

3. Go to **Caching** > **Configuration**
   - [ ] Caching Level: Standard
   - [ ] Browser Cache TTL: Respect Existing Headers

4. Go to **Rules** > **Transform Rules**
   - Consider adding rules for:
     - Static asset caching
     - URL normalization
     - Response headers

### Phase 5: DNS Migration and Cutover

#### Step 11: Update DNS Records (Final Cutover)

**⚠️ IMPORTANT: This step will cause your site to switch from Netlify to Cloudflare**

**Current Netlify DNS:**
```
A record: @ → <Netlify IP>
or
CNAME: @ → <your-site>.netlify.app
```

**New Cloudflare Pages DNS:**

If using Cloudflare DNS:
1. Go to **DNS** > **Records**
2. Update or create:
   ```
   CNAME  @  terraphim-ai.pages.dev  (Proxied)
   CNAME  www  terraphim-ai.pages.dev  (Proxied)
   ```

**DNS Propagation:**
- Changes can take 5 minutes to 48 hours
- Most changes propagate within 15-30 minutes
- Test with: `dig terraphim.ai` or `nslookup terraphim.ai`

#### Step 12: Monitor the Migration

1. Use multiple DNS checkers:
   - https://www.whatsmydns.net/#A/terraphim.ai
   - https://dnschecker.org/

2. Monitor Cloudflare Analytics:
   - Go to **Analytics & Logs** > **Traffic**
   - Watch for traffic increase

3. Check both old and new sites:
   - Netlify: `https://<your-site>.netlify.app`
   - Cloudflare: `https://terraphim.ai`

4. Monitor error rates:
   - Cloudflare dashboard → Analytics → Errors
   - Check for 404s or 500s

### Phase 6: Configure Build Triggers and Automation

#### Step 13: Set Up Automatic Deployments

Cloudflare Pages automatically deploys on git push to your production branch.

**Configure deployment settings:**

1. Go to **Settings** > **Builds & deployments**
2. Configure:
   - **Production branch:** `main` (or your default branch)
   - **Preview branches:** All branches (or specific pattern)
   - **Build caching:** Enabled (recommended)

3. **Deploy hooks** (optional):
   - Create a deploy hook for manual/external triggers
   - Go to **Settings** > **Builds & deployments** > **Deploy hooks**
   - Click **Add deploy hook**
   - Name it and select branch
   - Save the webhook URL for external systems

#### Step 14: Configure Branch Previews

Cloudflare Pages automatically creates preview deployments for branches and pull requests.

**Preview URL pattern:**
```
https://<branch-name>.terraphim-ai.pages.dev
https://<PR-number>.terraphim-ai.pages.dev
```

**Configure preview settings:**
1. Go to **Settings** > **Builds & deployments**
2. Under **Production branch deployment**, select behavior:
   - Deploy production branch only
   - Deploy all branches
   - Deploy based on pattern

---

## Configuration Files

### Files Created for Cloudflare Pages

#### 1. `.cloudflare-pages.toml`

This file contains Cloudflare Pages configuration:

```toml
[build]
command = "zola build"
destination = "public"

[build.environment]
ZOLA_VERSION = "0.14.1"
```

**Purpose:**
- Defines build command and output directory
- Sets environment variables
- Configures headers and redirects (if needed)

#### 2. `_headers`

This file defines custom HTTP headers:

```
/*
  X-Frame-Options: SAMEORIGIN
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  # ... more headers
```

**Purpose:**
- Security headers (CSP, X-Frame-Options, etc.)
- Cache control for static assets
- CORS headers if needed

### Files to Keep

- ✅ `netlify.toml` - Keep for now (for rollback capability)
- ✅ `config.toml` - Required by Zola
- ✅ All source files and content

### Files Generated

- `public/` - Build output (not committed to git, in .gitignore)

---

## DNS Setup

### DNS Configuration Matrix

| Record Type | Name | Value | Proxy Status | TTL |
|-------------|------|-------|--------------|-----|
| CNAME | @ | terraphim-ai.pages.dev | Proxied | Auto |
| CNAME | www | terraphim-ai.pages.dev | Proxied | Auto |
| TXT | @ | (existing verification records) | DNS only | Auto |

### DNS Verification Commands

Check DNS propagation:

```bash
# Check A record resolution
dig terraphim.ai A +short

# Check CNAME record
dig terraphim.ai CNAME +short

# Check with specific DNS server (Cloudflare)
dig @1.1.1.1 terraphim.ai

# Check from multiple locations
# Use: https://www.whatsmydns.net/#A/terraphim.ai
```

### SSL Certificate

Cloudflare Pages automatically provisions SSL certificates for custom domains.

**Verification:**
1. Visit `https://terraphim.ai`
2. Click the padlock icon in browser
3. View certificate details
4. Should show: Issued by Cloudflare

**Certificate details:**
- Type: Universal SSL (or Advanced Certificate Manager for paid plans)
- Coverage: terraphim.ai and www.terraphim.ai
- Auto-renewal: Enabled
- Edge certificates: Multiple per domain for redundancy

---

## Post-Migration Testing

### Functional Testing Checklist

#### Core Functionality
- [ ] Homepage loads correctly
- [ ] All navigation links work
- [ ] Internal page links function
- [ ] External links open in new tabs
- [ ] Dark mode toggle works
- [ ] Dark mode persistence (localStorage)
- [ ] Search modal opens
- [ ] Search functionality works
- [ ] Search results display correctly
- [ ] Pagination works (if applicable)
- [ ] 404 page displays correctly
- [ ] RSS feed is accessible at `/rss.xml`
- [ ] Sitemap is accessible at `/sitemap.xml`

#### Visual Testing
- [ ] CSS loads correctly
- [ ] Fonts render properly
- [ ] Images display correctly
- [ ] Icons show (FontAwesome)
- [ ] Responsive design works
- [ ] Mobile menu functions
- [ ] Layout is correct on various screen sizes

#### Performance Testing
- [ ] Page load time < 3 seconds
- [ ] Lighthouse score:
  - Performance: > 90
  - Accessibility: > 90
  - Best Practices: > 90
  - SEO: > 90
- [ ] No console errors
- [ ] All assets load from CDN

#### Security Testing
- [ ] HTTPS redirect works (http → https)
- [ ] SSL certificate is valid
- [ ] Security headers present
- [ ] CSP doesn't block legitimate resources
- [ ] No mixed content warnings

#### Browser Testing
Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

#### SEO Testing
- [ ] Meta tags present
- [ ] OpenGraph tags work
- [ ] Twitter Card tags work
- [ ] Canonical URLs correct
- [ ] Robots.txt accessible
- [ ] Sitemap.xml accessible
- [ ] Google Search Console still receiving data

### Performance Comparison

**Recommended Tools:**
- WebPageTest: https://www.webpagetest.org/
- Lighthouse: Built into Chrome DevTools
- GTmetrix: https://gtmetrix.com/
- Pingdom: https://tools.pingdom.com/

**Metrics to Compare (Netlify vs Cloudflare):**

| Metric | Netlify | Cloudflare Pages | Target |
|--------|---------|------------------|--------|
| TTFB (Time to First Byte) | | | < 200ms |
| First Contentful Paint | | | < 1.5s |
| Largest Contentful Paint | | | < 2.5s |
| Total Blocking Time | | | < 200ms |
| Cumulative Layout Shift | | | < 0.1 |
| Speed Index | | | < 3.0s |
| Total Page Size | | | Similar |
| Number of Requests | | | Similar |

### Analytics Setup

Ensure Google Analytics continues to work:

1. Check `config.toml`:
   ```toml
   [extra.analytics]
   google = "G-5KRW51RLEJ"
   ```

2. Visit site and verify tracking:
   - Open browser DevTools → Network tab
   - Look for requests to `google-analytics.com` or `googletagmanager.com`

3. Check Google Analytics Real-Time reports:
   - Should show your visit

4. **Optional:** Set up Cloudflare Web Analytics:
   - Go to Analytics & Logs → Web Analytics
   - Enable Cloudflare Web Analytics
   - Add beacon to your site (if desired)

---

## Rollback Plan

If issues occur during migration, you can rollback quickly.

### Emergency Rollback (DNS)

**Immediate rollback (fastest - 5-30 minutes):**

1. Go to Cloudflare DNS settings
2. Update DNS records back to Netlify:
   ```
   Change:
   CNAME @ terraphim-ai.pages.dev

   Back to:
   CNAME @ <your-site>.netlify.app
   ```
3. DNS will propagate within 5-30 minutes
4. Site will serve from Netlify again

### Rollback Checklist

- [ ] Announce rollback to team
- [ ] Change DNS records back to Netlify
- [ ] Verify Netlify site is still active and building
- [ ] Monitor DNS propagation
- [ ] Test site accessibility
- [ ] Document issues encountered
- [ ] Create action plan to resolve issues
- [ ] Schedule retry of migration

### Keeping Netlify Active During Migration

**Best Practice:** Keep Netlify active for 1-2 weeks after migration

1. Don't delete Netlify site immediately
2. Keep it as a backup
3. Netlify will continue to deploy from git (unless you disable it)
4. After confirming Cloudflare Pages is stable, you can:
   - Pause Netlify builds
   - Eventually delete Netlify site

---

## Differences from Netlify

### Feature Comparison

| Feature | Netlify | Cloudflare Pages | Notes |
|---------|---------|------------------|-------|
| **Hosting** | ✅ | ✅ | Both excellent |
| **Build System** | ✅ | ✅ | Similar functionality |
| **Custom Domains** | ✅ | ✅ | Both support HTTPS |
| **Deploy Previews** | ✅ | ✅ | Cloudflare: auto for all branches |
| **Edge Network** | ✅ Good | ✅ Excellent | Cloudflare has larger network |
| **DDoS Protection** | Basic | ✅ Enterprise-grade | Major Cloudflare advantage |
| **Analytics** | ✅ | ✅ | Both have built-in analytics |
| **Functions** | Netlify Functions | Cloudflare Workers | Different syntax, CF Workers more powerful |
| **Forms** | ✅ Built-in | ❌ Need Workers | Netlify easier for forms |
| **Identity** | ✅ Built-in | ❌ Need Workers | Netlify easier for auth |
| **Split Testing** | ✅ | ⚠️ Via Workers | Netlify easier |
| **Bandwidth** | Limited (100GB free) | ✅ Unlimited | Cloudflare advantage |
| **Build Minutes** | 300 min/month | ✅ Unlimited | Cloudflare advantage |
| **Deploy Hooks** | ✅ | ✅ | Both support |
| **Environment Variables** | ✅ | ✅ | Both support |
| **Custom Headers** | `_headers` file | `_headers` file | Same format! |
| **Redirects** | `_redirects` file | `_redirects` file | Same format! |
| **Git Integration** | ✅ GitHub, GitLab, Bitbucket | ✅ GitHub, GitLab | Both well-integrated |

### Syntax Differences

#### Headers File

**Netlify** `_headers`:
```
/*
  X-Frame-Options: DENY
```

**Cloudflare Pages** `_headers`:
```
/*
  X-Frame-Options: DENY
```

✅ **Same format!** No changes needed.

#### Redirects File

**Netlify** `_redirects`:
```
/old-path /new-path 301
```

**Cloudflare Pages** `_redirects`:
```
/old-path /new-path 301
```

✅ **Same format!** No changes needed.

#### Build Configuration

**Netlify** `netlify.toml`:
```toml
[build]
  command = "zola build"
  publish = "public"

[build.environment]
  ZOLA_VERSION = "0.14.1"
```

**Cloudflare Pages** `.cloudflare-pages.toml`:
```toml
[build]
  command = "zola build"
  destination = "public"

[build.environment]
  ZOLA_VERSION = "0.14.1"
```

⚠️ **Minor difference:** `publish` vs `destination`

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Build Fails on Cloudflare Pages

**Symptoms:**
- Build fails with error about Zola not found
- Error: "zola: command not found"

**Solutions:**
1. Check environment variable:
   - Verify `ZOLA_VERSION = 0.14.1` is set in project settings
   - Go to Settings → Environment variables

2. Check build command:
   - Should be exactly: `zola build`
   - Check for typos

3. Check build output directory:
   - Should be: `public`

4. Review build logs:
   - Look for specific error messages
   - Check if submodules are initialized

#### Issue 2: Custom Domain Not Working

**Symptoms:**
- Custom domain shows error page
- SSL certificate error
- DNS_PROBE_FINISHED_NXDOMAIN

**Solutions:**
1. Check DNS propagation:
   ```bash
   dig terraphim.ai
   nslookup terraphim.ai
   ```

2. Verify CNAME record:
   - Should point to: `terraphim-ai.pages.dev`
   - Should be proxied (orange cloud in Cloudflare)

3. Check SSL/TLS mode:
   - Should be: Full (strict)
   - Go to SSL/TLS → Overview

4. Wait for certificate provisioning:
   - Can take 5-15 minutes
   - Check status in Custom domains section

#### Issue 3: Assets Not Loading (404 errors)

**Symptoms:**
- CSS files return 404
- JavaScript files return 404
- Images don't load

**Solutions:**
1. Check build output:
   - Verify `public/` directory contains all assets
   - Check build logs for errors

2. Check base URL in config.toml:
   ```toml
   base_url = "https://terraphim.ai"
   ```

3. Clear Cloudflare cache:
   - Go to Caching → Configuration
   - Click "Purge Everything"

4. Check asset paths:
   - Should be relative or use `{{ get_url() }}` helper

#### Issue 4: Dark Mode Not Persisting

**Symptoms:**
- Dark mode toggle works but doesn't save preference
- Page reloads in light mode

**Solutions:**
1. Check browser console for localStorage errors
2. Verify site.js is loading correctly
3. Check Content-Security-Policy headers:
   - May need to allow localStorage access
4. Test in incognito mode (rules out extensions)

#### Issue 5: Search Not Working

**Symptoms:**
- Search modal opens but no results
- JavaScript errors in console

**Solutions:**
1. Check build_search_index in config.toml:
   ```toml
   build_search_index = true
   ```

2. Verify search index files exist:
   - `public/search_index.en.js`
   - `public/elasticlunr.min.js`

3. Check JavaScript loading order:
   - elasticlunr.min.js before site.js
   - search_index.en.js before site.js

#### Issue 6: High Latency on First Load

**Symptoms:**
- First page load is slow (TTFB > 1s)
- Subsequent loads are fast

**Solutions:**
1. Enable HTTP/3:
   - Go to Speed → Optimization
   - Enable HTTP/3 (with QUIC)

2. Enable Early Hints:
   - Go to Speed → Optimization
   - Enable Early Hints

3. Reduce DNS lookup time:
   - Ensure using Cloudflare nameservers

4. Check caching:
   - Verify Cache-Control headers are set
   - Use Cloudflare caching rules

#### Issue 7: Analytics Not Tracking

**Symptoms:**
- Google Analytics not showing data
- No page views recorded

**Solutions:**
1. Check Google Analytics ID in config.toml:
   ```toml
   [extra.analytics]
   google = "G-5KRW51RLEJ"
   ```

2. Check CSP headers:
   - Must allow `www.googletagmanager.com`
   - Check _headers file

3. Check network requests:
   - Open DevTools → Network
   - Look for requests to Google Analytics

4. Wait 24-48 hours:
   - Analytics data can be delayed

---

## Additional Resources

### Cloudflare Documentation

- **Cloudflare Pages Docs:** https://developers.cloudflare.com/pages/
- **Build Configuration:** https://developers.cloudflare.com/pages/platform/build-configuration/
- **Custom Domains:** https://developers.cloudflare.com/pages/platform/custom-domains/
- **Headers:** https://developers.cloudflare.com/pages/platform/headers/
- **Redirects:** https://developers.cloudflare.com/pages/platform/redirects/
- **Cloudflare Workers:** https://developers.cloudflare.com/workers/

### Zola Documentation

- **Zola Docs:** https://www.getzola.org/documentation/
- **Deployment:** https://www.getzola.org/documentation/deployment/overview/
- **Configuration:** https://www.getzola.org/documentation/getting-started/configuration/

### Performance & Security

- **Web.dev:** https://web.dev/
- **Lighthouse:** https://developers.google.com/web/tools/lighthouse
- **Security Headers:** https://securityheaders.com/
- **SSL Labs:** https://www.ssllabs.com/ssltest/

### Community & Support

- **Cloudflare Community:** https://community.cloudflare.com/
- **Cloudflare Discord:** https://discord.gg/cloudflaredev
- **Zola Discourse:** https://zola.discourse.group/

---

## Migration Timeline

### Recommended Timeline

**Week 1: Planning & Setup**
- Day 1-2: Review documentation, create Cloudflare account
- Day 3-4: Configure Cloudflare Pages, test build
- Day 5-7: Test deployment, verify functionality

**Week 2: Staging & Testing**
- Day 1-3: Comprehensive testing on Pages URL
- Day 4-5: Performance testing and optimization
- Day 6-7: Security testing and header configuration

**Week 3: DNS Migration**
- Day 1: Update DNS records (during low-traffic period)
- Day 2-3: Monitor traffic and errors
- Day 4-7: Final verification and optimization

**Week 4: Cleanup**
- Day 1-7: Monitor for issues, keep Netlify as backup

**Week 5+: Decommission Netlify**
- Once confident, pause/delete Netlify site

### Low-Risk Migration Strategy

For **zero-downtime migration**:

1. Keep Netlify running
2. Set up Cloudflare Pages with `.pages.dev` domain
3. Test extensively on Cloudflare
4. Switch DNS during low-traffic period (e.g., Sunday 2 AM)
5. Monitor closely for 24-48 hours
6. Keep Netlify active for 2 weeks as backup

---

## Success Criteria

Migration is considered successful when:

- ✅ Site is accessible at https://terraphim.ai
- ✅ All pages load correctly without errors
- ✅ Dark mode functions properly
- ✅ Search works as expected
- ✅ SSL certificate is valid and auto-renewing
- ✅ Performance metrics are equal or better than Netlify
- ✅ Lighthouse scores are 90+ in all categories
- ✅ No console errors in browser
- ✅ Analytics tracking is working
- ✅ All security headers are present
- ✅ Mobile responsiveness is maintained
- ✅ SEO rankings are stable or improved
- ✅ Automatic deployments work from Git
- ✅ Preview deployments work for branches/PRs
- ✅ No downtime experienced by users
- ✅ Team is confident in the new platform

---

## Conclusion

Migrating from Netlify to Cloudflare Pages offers significant benefits in terms of performance, security, and cost. This guide provides a comprehensive, step-by-step approach to ensure a smooth migration with minimal risk.

**Key Takeaways:**

1. **Preparation is crucial** - Test thoroughly before DNS cutover
2. **Use preview URLs** - Validate everything on .pages.dev before switching
3. **Keep Netlify active** - Maintain backup for easy rollback
4. **Monitor closely** - Watch analytics and errors after migration
5. **Gradual approach** - No need to rush, take time to test

**Need Help?**

- Cloudflare Support: https://support.cloudflare.com/
- Community Forums: https://community.cloudflare.com/
- Documentation: https://developers.cloudflare.com/

---

**Migration Status:** ⏳ Ready to begin
**Last Updated:** 2025-11-13
**Next Review:** After successful migration
