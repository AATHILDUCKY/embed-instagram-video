# Loop

A mobile-friendly Instagram reel collection. The application is a single `index.html` with inline CSS and JavaScript. No npm, frameworks, font downloads, API keys, or runtime CDN dependencies. Instagram's embedded player is the only third-party request.

## Add your reels

Edit `videos.json`. It contains **only an array of links**:

```json
[
  "https://www.instagram.com/reel/YOUR_FIRST_SHORTCODE/",
  "https://www.instagram.com/reel/YOUR_SECOND_SHORTCODE/"
]
```

Replace those examples with actual public Instagram links. `reel`, `reels`, and `p` links are accepted; tracking parameters are removed and duplicates are ignored. The first link appears first. The supplied file is intentionally empty, so the page shows its empty collection design until you add your content. Invalid links fail the deployment build with an explanation instead of publishing an incomplete collection.

## Preview locally

```sh
python3 -m http.server 8000
```

Open http://localhost:8000. Open through HTTP, not by double-clicking the HTML: browsers restrict fetching JSON from `file://`.

## Deploy on GitHub Pages

1. Push these files to the `main` branch of a GitHub repository.
2. In the repository's **Settings → Pages → Build and deployment**, set **Source** to **GitHub Actions**.
3. Run the **Build and deploy Loop** workflow (or push another commit). It builds and publishes `dist` automatically. Future changes to `videos.json` rebuild the HTML and sitemap.

The workflow obtains your actual Pages URL, including the repository subdirectory or configured custom domain, for canonical and sitemap URLs. If your branch is different, update the workflow's `branches` setting. No deployment has been performed by creating these files.

For a manual deployment:

```sh
python3 build.py --site-url https://YOUR_USERNAME.github.io/YOUR_REPOSITORY/
python3 -m http.server 8000 --directory dist
```

Publish the contents of `dist`. Customize the brand, title, description, and social metadata in `index.html` before publishing.

## Features and performance

- Responsive dark interface, touch controls, reduced-motion support, labeled buttons, visible keyboard focus, and safe-area padding.
- Six cards added per batch, automatic scroll loading, and a Load more button as a fallback.
- Embedded players loaded near the viewport, removed when far away to stop playback and limit memory; favorites stay in this browser's local storage.
- Save/unsave, saved collection, random discovery, previous/next controls, native sharing or copy link, and direct `#reel-SHORTCODE` links.
- Persistent “Watch on Instagram” links when the player cannot display content.
- Runtime JSON updates with a pre-rendered HTML fallback if fetching the collection fails.

Instagram controls its cross-origin player: this site cannot guarantee autoplay, custom playback controls, or video availability. Scrolling outside an iframe moves the feed; gestures inside the Instagram frame are handled by Instagram. Use the previous/next buttons as an alternative. Public content must allow embedding; private, removed, restricted, or embed-disabled posts may only show an error/login prompt. No video files, captions, creator names, thumbnails, or popularity counts are invented or scraped.

## SEO: what this delivers

The build writes **every reel card and Instagram link into the initial HTML**, including links beyond the first scroll batch. They work without JavaScript. It adds `CollectionPage`/`ItemList` structured data, canonical and Open Graph URLs, and a sitemap of the actual collection page. Page metadata is in the source HTML. Submit the published sitemap URL to Google Search Console. For GitHub project sites, `robots.txt` is served under the repository path; crawlers only use `/robots.txt` at the domain root, so submit the sitemap directly. A custom domain with this site at its root serves robots.txt in the correct location.

**A single page cannot provide independently indexable watch pages for every reel.** Fragment links support sharing/navigation but are not separate pages. A list of Instagram URLs also cannot supply the verified title, thumbnail, upload date, and description needed for useful `VideoObject` markup. Google may index the collection and discover the external links; it does not guarantee indexing each embedded video. Individually indexed videos would need separate watch URLs, descriptive content, and real video metadata, which exceeds a one-page, links-only setup.

References: [Google JavaScript SEO](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics), [video SEO](https://developers.google.com/search/docs/appearance/video), [lazy loading](https://developers.google.com/search/docs/crawling-indexing/javascript/lazy-loading), and [GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
