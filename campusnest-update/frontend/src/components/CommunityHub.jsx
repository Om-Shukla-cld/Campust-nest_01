import { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { useAuth } from '../App'
import { useToast } from './Toast'
import { Spinner, Empty, Modal } from './shared'

const ago = (d) => { const m = Math.round((Date.now() - new Date(d + (d.endsWith('Z') ? '' : 'Z'))) / 60000); return m < 60 ? `${m}m ago` : m < 1440 ? `${Math.round(m / 60)}h ago` : `${Math.round(m / 1440)}d ago` }

export default function CommunityHub() {
  const { user } = useAuth()
  const toast = useToast()
  const [groups, setGroups] = useState(null)
  const [active, setActive] = useState(null)  // null = feed
  const [posts, setPosts] = useState(null)
  const [compose, setCompose] = useState(null)
  const [open, setOpen] = useState(null)
  const [comment, setComment] = useState('')

  const loadGroups = () => api.getGroups().then(setGroups)
  const loadPosts = () => (active ? api.getGroupPosts(active) : api.getFeed()).then(setPosts).catch(e => toast(e.message, 'error'))
  useEffect(() => { loadGroups() }, [])
  useEffect(() => { setPosts(null); loadPosts() }, [active])

  const need = () => toast('Log in to participate', 'error')
  const like = async (p) => { if (!user) return need(); try { await api.likePost(p.id); loadPosts(); if (open?.id === p.id) api.getPost(p.id).then(setOpen) } catch (e) { toast(e.message, 'error') } }
  const join = async (g) => { if (!user) return need(); try { const r = await api.joinGroup(g.id); toast(r.message, 'success'); loadGroups() } catch (e) { toast(e.message, 'error') } }
  const flag = async (p) => { if (!user) return need(); try { await api.flagPost(p.id); toast('Reported to moderators') } catch (e) { toast(e.message, 'error') } }
  const send = async (e) => {
    e.preventDefault()
    try { await api.createPost({ ...compose, group_id: +compose.group_id, tags: String(compose.tags || '').split(',').map(s => s.trim()).filter(Boolean) }); toast('Posted!', 'success'); setCompose(null); loadPosts(); loadGroups() }
    catch (err) { toast(err.message, 'error') }
  }
  const addComment = async (e) => {
    e.preventDefault(); if (!user) return need()
    try { await api.commentOnPost(open.id, comment); setComment(''); api.getPost(open.id).then(setOpen); loadPosts() } catch (err) { toast(err.message, 'error') }
  }
  const f = (k) => ({ value: compose?.[k] ?? '', onChange: e => setCompose(x => ({ ...x, [k]: e.target.value })) })

  return (
    <div className="grid lg:grid-cols-4 gap-4">
      <aside className="space-y-2">
        <h1 className="text-2xl font-extrabold">Community 💬</h1>
        <button onClick={() => setActive(null)} className={`w-full text-left card py-3 ${active === null ? 'ring-2 ring-brand-500' : ''}`}>🏠 <b>Home feed</b></button>
        {!groups ? <Spinner /> : groups.map(g => (
          <div key={g.id} className={`card py-3 cursor-pointer ${active === g.id ? 'ring-2 ring-brand-500' : ''}`} onClick={() => setActive(g.id)}>
            <div className="flex items-center justify-between"><div className="font-semibold">{g.icon} {g.name}</div><button onClick={e => { e.stopPropagation(); join(g) }} className={`text-xs ${g.is_member ? 'text-slate-400' : 'text-brand-600 font-semibold'}`}>{g.is_member ? 'Joined' : 'Join'}</button></div>
            <div className="text-xs text-slate-500">{g.member_count} members · {g.post_count} posts</div>
          </div>
        ))}
      </aside>
      <section className="lg:col-span-3 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-lg">{active ? groups?.find(g => g.id === active)?.name : 'Latest across all groups'}</h2>
          <button className="btn-primary" onClick={() => user ? setCompose({ group_id: active || groups?.[0]?.id, title: '', content: '', tags: '' }) : need()}>+ New post</button>
        </div>
        {!posts ? <Spinner /> : posts.length === 0 ? <Empty>No posts yet. Start the conversation!</Empty> : posts.map(p => (
          <article key={p.id} className="card">
            <div className="flex items-center gap-2 text-xs text-slate-500"><span className="font-semibold text-slate-700">{p.author?.name}</span><span className="chip capitalize">{p.author?.role}</span><span>· {ago(p.created_at)}</span>{!active && <span>· {groups?.find(g => g.id === p.group_id)?.name}</span>}</div>
            {p.title && <h3 className="font-bold mt-1">{p.title}</h3>}
            <p className="text-sm text-slate-700 mt-1">{p.content}</p>
            <div className="flex flex-wrap gap-1 mt-2">{p.tags.map(t => <span key={t} className="chip">#{t}</span>)}</div>
            <div className="flex gap-3 mt-3 text-sm">
              <button onClick={() => like(p)} className="text-slate-600 hover:text-rose-600">❤️ {p.likes}</button>
              <button onClick={() => api.getPost(p.id).then(setOpen)} className="text-slate-600 hover:text-brand-600">💬 {p.comment_count}</button>
              <button onClick={() => flag(p)} className="ml-auto text-xs text-slate-400 hover:text-rose-600">🚩 report</button>
            </div>
          </article>
        ))}
      </section>

      <Modal open={!!compose} onClose={() => setCompose(null)} title="New post">
        {compose && (
          <form onSubmit={send} className="space-y-3">
            <div><label className="label">Group</label><select className="input" {...f('group_id')}>{groups?.map(g => <option key={g.id} value={g.id}>{g.icon} {g.name}</option>)}</select></div>
            <div><label className="label">Title</label><input className="input" {...f('title')} /></div>
            <div><label className="label">Content</label><textarea className="input" rows={4} required {...f('content')} /></div>
            <div><label className="label">Tags (comma separated)</label><input className="input" {...f('tags')} /></div>
            <div className="flex justify-end gap-2"><button type="button" className="btn-ghost" onClick={() => setCompose(null)}>Cancel</button><button className="btn-primary">Post</button></div>
          </form>
        )}
      </Modal>
      <Modal open={!!open} onClose={() => setOpen(null)} title={open?.title || 'Post'}>
        {open && (
          <div className="space-y-3">
            <div className="text-xs text-slate-500">{open.author?.name} · {ago(open.created_at)}</div>
            <p className="text-sm">{open.content}</p>
            <button onClick={() => like(open)} className="text-sm">❤️ {open.likes}</button>
            <div className="label">Comments ({open.comments.length})</div>
            <div className="space-y-2">{open.comments.map(c => <div key={c.id} className="bg-slate-50 rounded-xl p-2 text-sm"><b>{c.author?.name}</b> <span className="text-slate-600">{c.content}</span></div>)}</div>
            <form onSubmit={addComment} className="flex gap-2"><input className="input" placeholder="Write a comment…" value={comment} onChange={e => setComment(e.target.value)} required /><button className="btn-primary">Send</button></form>
          </div>
        )}
      </Modal>
    </div>
  )
}
