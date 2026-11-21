#!/usr/bin/env node
// Tell search engines which pages changed, through IndexNow (indexnow.org).
//
// Bing, and through it ChatGPT search and Copilot, otherwise find a new or
// changed page whenever they next happen to crawl it. IndexNow lets the site
// say "these URLs changed" straight away. One submission is shared with every
// participating engine.
//
// What it does on each run:
//   1. Reads the live sitemap.
//   2. Gives every URL a fingerprint: the sitemap's lastmod where that can be
//      trusted, otherwise a hash of the page's visible text.
//   3. Compares the fingerprints with the ones saved by the previous run.
//   4. Submits only the URLs that were added, changed or removed.
//   5. Saves the new fingerprints, but only if the submission succeeded, so a
//      failed run is retried by the next one.
//
// The first run has nothing to compare with, so it saves the fingerprints and
// submits nothing, unless INDEXNOW_SUBMIT_ALL=true.
//
// No dependencies: Node 20 or later. Configuration is by environment variable:
//   INDEXNOW_HOST           limacharlie.io
//   INDEXNOW_KEY            the key; https://<host>/<key>.txt must serve it
//   INDEXNOW_SITEMAP        default https://<host>/sitemap.xml
//   INDEXNOW_TRUST_LASTMOD  "true" when the sitemap's lastmod is a real date
//   INDEXNOW_STATE          default .indexnow/<host>.json
//   INDEXNOW_SUBMIT_ALL     "true" to submit every URL (first run)
//   INDEXNOW_DRY_RUN        "true" to do everything except submit and save
//   INDEXNOW_CACHE_BUST     "true" to add a throwaway query string to every fetch, for
//                           hosts whose CDN keeps serving the old page after a deploy
import { createHash } from 'node:crypto'
import { mkdir, readFile, writeFile, appendFile } from 'node:fs/promises'
import { dirname } from 'node:path'
import { pathToFileURL } from 'node:url'

const ENDPOINT = 'https://api.indexnow.org/indexnow'
const MAX_URLS_PER_REQUEST = 10000 // the protocol's limit
const CONCURRENCY = 8
const REQUEST_TIMEOUT_MS = 20000
const USER_AGENT = 'limacharlie-indexnow/1.0'

/** The <loc> and <lastmod> of every <url> in a sitemap. */
export const parseSitemap = (xml) =>
  [...xml.matchAll(/<url>([\s\S]*?)<\/url>/g)].flatMap(([, body]) => {
    const loc = body.match(/<loc>([^<]+)<\/loc>/)
    if (!loc) return []
    const lastmod = body.match(/<lastmod>([^<]+)<\/lastmod>/)
    const decode = (text) => text.trim().replace(/&amp;/g, '&')
    return [{ loc: decode(loc[1]), lastmod: lastmod ? lastmod[1].trim() : undefined }]
  })

const without = (html, tags) =>
  tags.reduce(
    (text, tag) => text.replace(new RegExp(`<${tag}[\\s>][\\s\\S]*?</${tag}>`, 'gi'), ' '),
    html,
  )

/**
 * The visible text of a page's main content, whitespace collapsed.
 *
 * Scripts, styles and markup are dropped because they change on every deploy
 * (build ids, hashed class names and asset URLs) without the page's content
 * changing. The content is the <article>, else the <main>, else the <body>
 * with its <header>, <nav> and <footer> removed.
 */
export const extractText = (html) => {
  const cleaned = without(html.replace(/<!--[\s\S]*?-->/g, ' '), [
    'script',
    'style',
    'noscript',
    'svg',
    'template',
  ])
  let content
  for (const tag of ['article', 'main']) {
    const match = cleaned.match(new RegExp(`<${tag}[\\s>][\\s\\S]*</${tag}>`, 'i'))
    if (match) {
      content = match[0]
      break
    }
  }
  if (!content) {
    const body = cleaned.match(/<body[\s>][\s\S]*<\/body>/i)
    content = without(body ? body[0] : cleaned, ['header', 'nav', 'footer'])
  }
  return content
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

export const hashText = (text) => createHash('sha256').update(text).digest('hex').slice(0, 32)

/**
 * What changed between two runs. `previous` is null on the first run: then
 * nothing counts as changed, because there is nothing to compare with.
 */
export const diffFingerprints = (previous, current) => {
  if (!previous) return { added: [], changed: [], removed: [] }
  const added = []
  const changed = []
  for (const [url, fingerprint] of Object.entries(current)) {
    if (!(url in previous)) added.push(url)
    else if (previous[url] !== fingerprint) changed.push(url)
  }
  const removed = Object.keys(previous).filter((url) => !(url in current))
  return { added, changed, removed }
}

export const chunk = (items, size) =>
  Array.from({ length: Math.ceil(items.length / size) }, (_, i) =>
    items.slice(i * size, (i + 1) * size),
  )

export const buildPayload = (host, key, urlList) => ({
  host,
  key,
  keyLocation: `https://${host}/${key}.txt`,
  urlList,
})

// A throwaway query string makes a CDN fetch the page from its origin. Only
// the fetch uses it: the URLs submitted are the ones in the sitemap.
const cacheBust = process.env.INDEXNOW_CACHE_BUST === 'true' ? `indexnow=${Date.now()}` : ''
const busted = (url) => (cacheBust ? `${url}${url.includes('?') ? '&' : '?'}${cacheBust}` : url)

const fetchText = async (url) => {
  const response = await fetch(busted(url), {
    redirect: 'manual',
    headers: { 'User-Agent': USER_AGENT },
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  })
  return { status: response.status, text: response.status === 200 ? await response.text() : '' }
}

const mapWithConcurrency = async (items, limit, fn) => {
  const results = new Array(items.length)
  let next = 0
  const worker = async () => {
    while (next < items.length) {
      const index = next
      next += 1
      results[index] = await fn(items[index])
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker))
  return results
}

/**
 * A fingerprint for every URL. A page that cannot be fetched keeps the
 * fingerprint it had, so a timeout is never reported as a change.
 */
export const fingerprintAll = async (
  entries,
  { trustLastmod, previous, fetchPage = fetchText },
) => {
  let failed = 0
  const pairs = await mapWithConcurrency(entries, CONCURRENCY, async ({ loc, lastmod }) => {
    if (trustLastmod && lastmod) return [loc, `lastmod:${lastmod}`]
    try {
      const { status, text } = await fetchPage(loc)
      return [loc, status === 200 ? `text:${hashText(extractText(text))}` : `status:${status}`]
    } catch {
      failed += 1
      return previous && loc in previous ? [loc, previous[loc]] : null
    }
  })
  return { fingerprints: Object.fromEntries(pairs.filter(Boolean)), failed }
}

const readState = async (path) => {
  try {
    return JSON.parse(await readFile(path, 'utf8')).urls ?? null
  } catch {
    return null
  }
}

const main = async () => {
  const env = process.env
  const host = env.INDEXNOW_HOST
  const key = env.INDEXNOW_KEY
  if (!host || !key) throw new Error('INDEXNOW_HOST and INDEXNOW_KEY are required')
  const sitemapUrl = env.INDEXNOW_SITEMAP || `https://${host}/sitemap.xml`
  const statePath = env.INDEXNOW_STATE || `.indexnow/${host}.json`
  const trustLastmod = env.INDEXNOW_TRUST_LASTMOD === 'true'
  const submitAll = env.INDEXNOW_SUBMIT_ALL === 'true'
  const dryRun = env.INDEXNOW_DRY_RUN === 'true'

  const sitemap = await fetchText(sitemapUrl)
  if (sitemap.status !== 200) throw new Error(`${sitemapUrl} answered ${sitemap.status}`)
  const entries = parseSitemap(sitemap.text).filter(({ loc }) => new URL(loc).host === host)
  if (entries.length === 0) throw new Error(`${sitemapUrl} lists no URLs on ${host}`)

  const previous = await readState(statePath)
  const { fingerprints, failed } = await fingerprintAll(entries, { trustLastmod, previous })
  const { added, changed, removed } = diffFingerprints(previous, fingerprints)
  const urls = submitAll ? Object.keys(fingerprints) : [...added, ...changed, ...removed]

  const lines = [
    `### IndexNow: ${host}`,
    '',
    `- URLs in the sitemap: ${entries.length}`,
    `- Previous run on record: ${previous ? 'yes' : 'no (first run)'}`,
    `- Added: ${added.length}, changed: ${changed.length}, removed: ${removed.length}`,
    `- Pages that could not be fetched: ${failed}`,
    `- To submit: ${urls.length}${submitAll ? ' (every URL, as requested)' : ''}${dryRun ? ' (dry run: nothing sent)' : ''}`,
    '',
    ...urls.slice(0, 50).map((url) => `  - ${url}`),
    ...(urls.length > 50 ? [`  - and ${urls.length - 50} more`] : []),
  ]
  console.log(lines.join('\n'))
  if (env.GITHUB_STEP_SUMMARY) await appendFile(env.GITHUB_STEP_SUMMARY, `${lines.join('\n')}\n\n`)

  if (dryRun) return

  if (urls.length > 0) {
    // Engines fetch the key file to check the submission is from the site
    // owner. Check it first: without it every URL would be rejected.
    const keyUrl = `https://${host}/${key}.txt`
    const keyFile = await fetchText(keyUrl)
    if (keyFile.status !== 200 || keyFile.text.trim() !== key) {
      throw new Error(
        `${keyUrl} does not serve the key (status ${keyFile.status}); nothing was submitted`,
      )
    }
    for (const batch of chunk(urls, MAX_URLS_PER_REQUEST)) {
      const response = await fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json; charset=utf-8', 'User-Agent': USER_AGENT },
        body: JSON.stringify(buildPayload(host, key, batch)),
        signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
      })
      // 200: received. 202: received, key validation pending.
      if (response.status !== 200 && response.status !== 202) {
        throw new Error(
          `IndexNow answered ${response.status} for ${batch.length} URLs; state not saved, the next run retries`,
        )
      }
      console.log(`submitted ${batch.length} URLs: ${response.status}`)
    }
  }

  await mkdir(dirname(statePath), { recursive: true })
  await writeFile(
    statePath,
    `${JSON.stringify({ host, savedAt: new Date().toISOString(), urls: fingerprints })}\n`,
  )
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    console.error(error.message)
    process.exit(1)
  })
}
