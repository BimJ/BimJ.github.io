export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(204).end();

  try {
    if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

    const token = process.env.GITHUB_TOKEN;
    const owner = process.env.GITHUB_OWNER;
    const repo = process.env.GITHUB_REPO;
    const branch = process.env.GITHUB_BRANCH || 'main';

    if (!token || !owner || !repo) {
      return res.status(500).json({ error: 'Server not configured (missing env vars)' });
    }

    const { date, payload } = req.body || {};
    if (!date || !payload) return res.status(400).json({ error: 'Missing date or payload' });

    const path = `data/schedules/${date}.json`;
    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${encodeURIComponent(path)}`;

    // Build content
    const contentStr = JSON.stringify(payload, null, 2);
    const contentBase64 = Buffer.from(contentStr, 'utf8').toString('base64');

    // Check if file exists to get sha
    const getRes = await fetch(`${apiUrl}?ref=${encodeURIComponent(branch)}`, {
      headers: { Accept: 'application/vnd.github.v3+json', Authorization: `token ${token}` }
    });

    let sha = null;
    if (getRes.status === 200) {
      const getData = await getRes.json();
      sha = getData.sha;
    } else if (getRes.status !== 404) {
      const txt = await getRes.text();
      return res.status(500).json({ error: 'GitHub API error (get): ' + txt });
    }

    const putBody = {
      message: `Uppdatera schema ${date}`,
      content: contentBase64,
      branch
    };
    if (sha) putBody.sha = sha;

    const putRes = await fetch(apiUrl, {
      method: 'PUT',
      headers: { Accept: 'application/vnd.github.v3+json', Authorization: `token ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(putBody)
    });

    if (!putRes.ok) {
      const text = await putRes.text();
      return res.status(500).json({ error: 'GitHub API error (put): ' + text });
    }

    const putData = await putRes.json();
    return res.status(200).json({ ok: true, path: putData.content && putData.content.path });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: String(err) });
  }
}
