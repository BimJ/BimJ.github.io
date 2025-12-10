export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(204).end();

  try {
    const owner = process.env.GITHUB_OWNER;
    const repo = process.env.GITHUB_REPO;
    const branch = process.env.GITHUB_BRANCH || 'main';
    if (!owner || !repo) return res.status(500).json({ error: 'Server not configured' });

    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/data/schedules?ref=${encodeURIComponent(branch)}`;
    const token = process.env.GITHUB_TOKEN;
    const headers = { Accept: 'application/vnd.github.v3+json' };
    if (token) headers.Authorization = `token ${token}`;

    const r = await fetch(apiUrl, { headers });
    if (r.status === 404) return res.status(200).json({ files: [] });
    if (!r.ok) {
      const txt = await r.text();
      return res.status(500).json({ error: 'GitHub API error: ' + txt });
    }
    const data = await r.json();
    const files = (Array.isArray(data) ? data : []).map(f => {
      const m = (f.name || '').match(/(\d{4}-\d{2}-\d{2})/);
      return { name: f.name, path: f.path, date: m ? m[1] : null, sha: f.sha, download_url: f.download_url };
    });
    return res.status(200).json({ files });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: String(err) });
  }
}
