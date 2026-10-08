import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Pause, Play } from "lucide-react";
import { findPerson } from "../../Políticos/interfaz/datos/catalogo";
import { Portrait } from "../../Políticos/interfaz/Retrato";
import Sources from "../../src/app/Sources";
import { dateLabel } from "./government-model";
import { senateChronology, senateLegislatures, senateSources, senatorGroups, type SenateTerm } from "./senate-model";

function SenateHemicycle({ groups }: { groups: ReturnType<typeof senatorGroups> }) {
  const [selected, setSelected] = useState<string | null>(null);
  const total = groups.reduce((sum, g) => sum + g.members.length, 0);
  const seats = groups.flatMap((g) => g.members.map(() => g.name));
  const rowWeights = [32, 38, 44, 50, 56, 62, 68];
  const counts = rowWeights.map((n) => Math.floor(total * n / 350));
  for (let i = 0; counts.reduce((a, b) => a + b, 0) < total; i++) counts[6 - i % 7]++;
  const points = counts.flatMap((count, row) => Array.from({ length: count }, (_, i) => {
    const radius = 75 + row * 19, angle = Math.PI - Math.PI * i / Math.max(1, count - 1);
    return { x: 250 + Math.cos(angle) * radius, y: 235 - Math.sin(angle) * radius, angle, row };
  })).sort((a, b) => b.angle - a.angle || a.row - b.row);
  const colors = ["#4177a8", "#bd5153", "#6b966d", "#c8a453", "#8f75ad", "#619d9e", "#9e8a75", "#7c8798"];
  const color = (name: string) => colors[groups.findIndex((g) => g.name === name) % colors.length];
  return <section className="hemicycle senate-hemicycle"><h3>Hemiciclo del Senado</h3>
    <svg viewBox="0 0 500 260" role="img" aria-label={`Esquema de ${total} mandatos del Senado documentados en esta fecha`}>
      {points.map((p, i) => <circle key={i} cx={p.x} cy={p.y} r={4.1} fill={color(seats[i])} opacity={selected && selected !== seats[i] ? .2 : 1}><title>{seats[i]}</title></circle>)}
      <text x={250} y={223} textAnchor="middle" fill="var(--text)" fontSize={26}>{total}</text>
      <text x={250} y={243} textAnchor="middle" fill="var(--muted)" fontSize={10}>MANDATOS DOCUMENTADOS</text>
    </svg>
    <div className="seat-legend">{groups.map((g) => <button key={g.name} aria-pressed={selected === g.name} onClick={() => setSelected(selected === g.name ? null : g.name)}><i style={{ background: color(g.name) }} /><span>{g.name}</span><b>{g.members.length}</b></button>)}</div>
    <p className="small-note">Distribución esquemática por grupos conservados en las fichas individuales; no reproduce los asientos físicos.</p>
  </section>;
}

export default function Senate({ selectedSnapshot, openSenate, openPerson, active = true }: {
  selectedSnapshot?: string; openSenate: (id: string) => void;
  openPerson: (id: string) => void; active?: boolean;
}) {
  const [mode, setMode] = useState<"legislatures" | "timeline">("legislatures");
  const [position, setPosition] = useState(() => {
    const index = senateChronology.findIndex((c) => c.id === selectedSnapshot);
    return index < 0 ? senateChronology.length - 1 : index;
  });
  const [playing, setPlaying] = useState(false);
  useEffect(() => {
    setPlaying(false);
    if (!active) return;
    const index = senateChronology.findIndex((c) => c.id === selectedSnapshot);
    setPosition(index < 0 ? senateChronology.length - 1 : index);
  }, [selectedSnapshot, active]);
  const current = senateChronology[position];
  const steps = mode === "timeline" ? senateChronology : senateChronology.filter((s) => s.legislature.id === current?.legislature.id);
  const localPosition = steps.findIndex((s) => s.id === current?.id);
  useEffect(() => {
    if (!playing || !active) return;
    if (localPosition >= steps.length - 1) { setPlaying(false); return; }
    const timer = setTimeout(() => setPosition(senateChronology.findIndex((s) => s.id === steps[localPosition + 1].id)), 1800);
    return () => clearTimeout(timer);
  }, [playing, active, position, mode]);
  if (!current) return <p className="small-note">No hay composiciones documentadas.</p>;
  const legislature = current.legislature;
  function choose(id: string) {
    const index = senateChronology.findIndex((s) => s.id === id);
    if (index < 0) return;
    setPlaying(false); setPosition(index); openSenate(id);
  }
  function person(id: string) {
    if (selectedSnapshot !== current.id) openSenate(current.id);
    openPerson(id);
  }
  const node = (member: SenateTerm) => {
    const p = findPerson(member.person);
    return <button key={`${member.person}-${member.role}-${member.organ}`} className="government-node" onClick={() => person(member.person)} aria-label={`Ficha de ${p?.name ?? member.name}, ${member.role}, ${member.organ}`}>
      <div className="government-portrait">{p ? <Portrait person={p} /> : <span>{member.name.slice(0, 2)}</span>}</div>
      <div><small>{member.role.toLocaleLowerCase("es")}</small><strong>{p?.name ?? member.name}</strong><span className="senate-term-date">{member.start ? dateLabel(member.start) : "Alta no publicada"}{member.end ? ` – ${dateLabel(member.end)}` : " · último registro"}</span></div>
    </button>;
  };
  const board = current.members.filter((m) => /MESA DEL SENADO/i.test(m.organ));
  const president = board.filter((m) => /^PRESIDENT[EA](?:\s|$)/i.test(m.role));
  const ordinal = (term: SenateTerm) => /PRIMER/i.test(term.role) ? 1 : /SEGUND/i.test(term.role) ? 2 : /TERCER/i.test(term.role) ? 3 : /CUART/i.test(term.role) ? 4 : 5;
  const vice = board.filter((m) => /^VICEPRESIDENT/i.test(m.role)).sort((a, b) => ordinal(a) - ordinal(b));
  const secretaries = board.filter((m) => /^SECRETARI/i.test(m.role)).sort((a, b) => ordinal(a) - ordinal(b));
  const spokespeople = current.members.filter((m) => /^PORTAVOZ$/i.test(m.role) && /^GRUPO PARLAMENTARIO/i.test(m.organ));
  const commissions = current.members.filter((m) => /^PRESIDENT[EA](?:\s|$)/i.test(m.role) && /^COMISI[ÓO]N/i.test(m.organ));
  const groups = senatorGroups(legislature, current.date);
  const undated = legislature.terms.filter((term) => !term.start);
  const isLastRecord = current.id === senateChronology.filter((s) => s.legislature.id === legislature.id).at(-1)?.id;
  return <div className="government-archive senate-archive">
    <div className="government-toolbar">
      <div className="archive-tabs" role="group" aria-label="Vista del Senado">
        <button aria-pressed={mode === "legislatures"} onClick={() => { setMode("legislatures"); setPlaying(false); }}>Por legislaturas</button>
        <button aria-pressed={mode === "timeline"} onClick={() => { setMode("timeline"); setPlaying(false); }}>Cronología</button>
      </div>
      <select aria-label="Elegir legislatura del Senado" value={legislature.id} onChange={(e) => choose(senateChronology.filter((s) => s.legislature.id === e.target.value).at(-1)!.id)}>
        {senateLegislatures.map((leg) => <option key={leg.id} value={leg.id}>{leg.label} · {leg.start.slice(0, 4)}</option>)}
      </select>
    </div>
    {mode === "legislatures" && <div className="government-library" aria-label="Biblioteca de legislaturas del Senado">
      {senateLegislatures.map((leg) => <button key={leg.id} className={leg.id === legislature.id ? "active" : ""} onClick={() => choose(senateChronology.filter((s) => s.legislature.id === leg.id).at(-1)!.id)}><span>{leg.start.slice(0, 4)}</span><strong>{leg.label}</strong></button>)}
    </div>}
    <section className="government-time">
      <div className="time-heading"><div><span>Senado · {legislature.label}</span><h2 aria-live="polite">{dateLabel(current.date)}</h2></div>
        <button className="icon-button" aria-label={playing ? "Pausar cronología del Senado" : "Reproducir cronología del Senado"} disabled={localPosition === steps.length - 1 && !playing} onClick={() => setPlaying(!playing)}>{playing ? <Pause size={18} /> : <Play size={18} />}</button>
      </div>
      <div className="timeline-control">
        <button className="icon-button" aria-label="Composición anterior del Senado" disabled={localPosition <= 0} onClick={() => choose(steps[localPosition - 1].id)}><ChevronLeft size={17} /></button>
        <input type="range" min={0} max={steps.length - 1} value={localPosition} aria-label="Fecha del registro del Senado" aria-valuetext={dateLabel(current.date)} onChange={(e) => choose(steps[Number(e.target.value)].id)} />
        <button className="icon-button" aria-label="Composición siguiente del Senado" disabled={localPosition === steps.length - 1} onClick={() => choose(steps[localPosition + 1].id)}><ChevronRight size={17} /></button>
      </div>
      <div className="time-extents"><span>{dateLabel(steps[0].date)}</span><span>{dateLabel(steps.at(-1)!.date)}</span></div>
      {legislature.number === 15 && <p className="small-note">Composiciones anteriores a la disolución del 6 de octubre de 2026. Desde la disolución, las funciones de la Mesa corresponden a la Mesa de la Diputación Permanente.</p>}
    </section>
    <div className="government-organigram" key={current.id}>
      <div className="president-tier">{president.map(node)}</div>
      <section className="government-tier"><h3>Vicepresidencias del Senado</h3><div className="vice-tier">{vice.map(node)}</div></section>
      <section className="government-tier"><h3>Secretarías de la Mesa</h3><div className="minister-tier">{secretaries.map(node)}</div></section>
      {!board.length && <p className="small-note">No hay miembros de la Mesa con fechas contrastadas para este punto de la cronología.</p>}
      {!!spokespeople.length && <section className="government-tier"><h3>Portavoces de los grupos</h3><p className="small-note">Cada portavoz representa a su grupo; las líneas agrupan órganos y no indican subordinación política.</p><div className="minister-tier">{spokespeople.map((m) => <div className="senate-group-node" key={m.person + m.organ}><h4>{m.organ}</h4>{node(m)}</div>)}</div></section>}
      {!!commissions.length && <section className="government-tier"><h3>Presidencias de comisión</h3><div className="minister-tier">{commissions.map((m) => <div className="senate-group-node" key={m.person + m.organ}><h4>{m.organ}</h4>{node(m)}</div>)}</div></section>}
    </div>
    <section className="senate-plenary government-tier"><h3>Composición del Pleno</h3>
      <p className="small-note">Mandatos individuales que incluyen esta fecha. Los grupos corresponden a la última adscripción conservada por la cámara en cada ficha; los traslados internos de grupo no se reconstruyen sin fechas acreditadas.</p>
      <SenateHemicycle groups={groups} />
      {groups.map((g) => <details className="senate-senators" key={g.name}><summary>{g.name} · {g.members.length}</summary><div className="senate-member-list">{g.members.map((m) => <button key={m.person} className="inline-link" onClick={() => person(m.person)}>{findPerson(m.person)?.name ?? m.name}</button>)}</div></details>)}
    </section>
    {isLastRecord && !!undated.length && <details className="senate-senators"><summary>Cargos sin fecha individual publicada</summary><p className="small-note">Último registro consultado el {dateLabel(legislature.checkedAt)}. Estos cargos se conservan fuera de la cronología porque la fuente no publica su fecha de alta.</p><div className="minister-tier">{undated.map((m) => <div className="senate-group-node" key={m.person + m.role + m.organ}><h4>{m.organ}</h4>{node(m)}<a className="inline-link" href={m.source} target="_blank" rel="noreferrer">Ficha del Senado</a></div>)}</div></details>}
    {!!legislature.incidents.length && <p className="small-note">Hay {legislature.incidents.length} registros con fechas contradictorias en la fuente individual. Esos intervalos se han excluido de la cronología.</p>}
    <Sources sources={senateSources(legislature)} />
  </div>;
}
