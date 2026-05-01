import { useState, useEffect } from 'react';
import { Robot, Gripper, ValidationResult } from './types';
import { getRobots as getAllRobots, getGrippers as getAllGrippers, validate, downloadReport } from './services/api';
import { KnowledgeTip, getKnowledgeTips, addKnowledgeTip, deleteKnowledgeTip, getLicense } from './services/api';

interface SystemSuggestion {
  robot: Robot;
  gripper: Gripper;
  plc: any;
  vision: any;
  sensor: any;
  pneumatic: any;
  feeder: any;
  safety_system: any;
  safety_housing: any;
  operating_angle_deg: number;
  operating_direction: string;
  total_price: number;
  delivery_weeks: number;
  compatibility: {
    robot_gripper: string;
    robot_plc: string;
    plc_vision: string;
    plc_feeder: string;
    plc_safety: string;
    protocols_used: string[];
  };
}

function JuniorDashboard() {
  const [selectedSystem, setSelectedSystem] = useState<SystemSuggestion | null>(null);
  const [workpieceMass, setWorkpieceMass] = useState(0.5);
  const [targetDistance, setTargetDistance] = useState(0.3);
  const [projectName, setProjectName] = useState('Projekt');
  const [result, setResult] = useState<ValidationResult & { knowledge_tips?: KnowledgeTip[] } | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [picksPerMinute, setPicksPerMinute] = useState(60);
  const [suggestions, setSuggestions] = useState<SystemSuggestion[]>([]);
  const [operatingAngle, setOperatingAngle] = useState(180);
  const [operatingDirection, setOperatingDirection] = useState('front');
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
  }, []);

  const handleFindSystems = async () => {
    if (workpieceMass <= 0 || targetDistance <= 0) return;
    setLoading(true);
    try {
      const res = await fetch('/api/v1/suggest-systems', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workpiece_mass_kg: workpieceMass,
          pick_place_distance_m: targetDistance,
          picks_per_minute: picksPerMinute,
          operating_angle_deg: operatingAngle,
          operating_direction: operatingDirection
        })
      });
      const data = await res.json();
      setSuggestions(data.suggestions || []);
      setStep(2);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSystem = (system: SystemSuggestion) => {
    setSelectedSystem(system);
    setStep(3);
  };

  const handleValidate = async () => {
    if (!selectedSystem) return;
    setLoading(true);
    try {
      const res = await validate(selectedSystem.robot.id, selectedSystem.gripper.id, workpieceMass, targetDistance, false);
      setResult(res);
      setStep(4);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!selectedSystem) return;
    setLoading(true);
    try {
      const blob = await downloadReport(
        selectedSystem.robot.id,
        selectedSystem.gripper.id,
        workpieceMass,
        targetDistance,
        false,
        projectName,
        selectedSystem.vision?.id,
        selectedSystem.sensor?.id,
        selectedSystem.pneumatic?.id,
        selectedSystem.feeder?.id,
        selectedSystem.safety_system?.id,
        selectedSystem.operating_angle_deg,
        selectedSystem.operating_direction
      );
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Technisches_Audit_${projectName}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (e) {
      console.error('Failed:', e);
    } finally {
      setLoading(false);
    }
  };

  const getUtilizationColor = (percent: number) => {
    if (percent <= 70) return 'green';
    if (percent <= 90) return 'yellow';
    return 'red';
  };

  const tipsForSelection = result?.knowledge_tips?.filter(t => t.target_id === selectedSystem?.robot.id || t.target_id === selectedSystem?.gripper.id || t.target_id === 'all') || [];

  return (
    <div>
      <div className="wizard-steps">
        <div className={`step ${step >= 1 ? (step > 1 ? 'completed' : 'active') : ''}`}><span className="step-number">1</span>Anforderungen</div>
        <div className={`step ${step >= 2 ? (step > 2 ? 'completed' : 'active') : ''}`}><span className="step-number">2</span>Systeme</div>
        <div className={`step ${step >= 3 ? (step > 3 ? 'completed' : 'active') : ''}`}><span className="step-number">3</span>Validierung</div>
      </div>

      <div className="main-content">
        <div className="card">
          <h2>Anforderungen eingeben</h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: 16 }}>Geben Sie Ihre Anforderungen ein - wir berechnen die passenden Systeme für Sie.</p>

          <div className="form-group">
            <label>Werkstück Gewicht (kg)</label>
            <input type="number" step="0.01" min="0.01" value={workpieceMass} onChange={(e) => setWorkpieceMass(parseFloat(e.target.value) || 0)} />
          </div>

          <div className="form-group">
            <label>Pick → Place Distanz (m)</label>
            <input type="number" step="0.01" min="0.01" value={targetDistance} onChange={(e) => setTargetDistance(parseFloat(e.target.value) || 0)} />
          </div>

          <div className="form-group">
            <label>Throughput (Picks/min)</label>
            <input type="number" step="1" min="1" value={picksPerMinute} onChange={(e) => setPicksPerMinute(parseInt(e.target.value) || 60)} />
          </div>

          <button onClick={() => setShowAdvanced(!showAdvanced)} style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', fontSize: '0.8rem', marginBottom: 8 }}>
            {showAdvanced ? '▲ Weniger' : '▶ Erweitert'}
          </button>

          {showAdvanced && (
            <div style={{ padding: 12, background: 'rgba(0,0,0,0.03)', borderRadius: 4, marginBottom: 12 }}>
              <div className="form-group">
                <label>Arbeitsbereich Winkel</label>
                <select value={operatingAngle} onChange={(e) => setOperatingAngle(parseInt(e.target.value))}>
                  <option value={90}>90°</option>
                  <option value={180}>180°</option>
                  <option value={270}>270°</option>
                  <option value={360}>360°</option>
                </select>
              </div>
              <div className="form-group">
                <label>Arbeitsbereich Richtung</label>
                <select value={operatingDirection} onChange={(e) => setOperatingDirection(e.target.value)}>
                  <option value="front">Vorne</option>
                  <option value="left">Links</option>
                  <option value="right">Rechts</option>
                  <option value="back">Hinten</option>
                </select>
              </div>
            </div>
          )}

          <button className="btn btn-primary" onClick={handleFindSystems} disabled={loading || workpieceMass <= 0 || targetDistance <= 0} style={{ width: '100%' }}>
            {loading ? 'Berechne...' : 'Passende Systeme finden'}
          </button>

          {suggestions.length > 0 && step >= 2 && (
            <div style={{ marginTop: 20 }}>
              <h3 style={{ marginBottom: 12 }}>Empfohlene Systeme (Top 3)</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: 12 }}>Basierend auf Ihren Anforderungen haben wir folgende kompatible 9-Teile-Systeme berechnet:</p>
              {suggestions.map((sys, index) => (
                <div key={index} className="checkbox-item" style={{ marginBottom: 12, padding: 12, border: '1px solid var(--border)', borderRadius: 8 }}>
                  <input type="radio" name="system-selection" id={`sys-${index}`} checked={selectedSystem === sys} onChange={() => handleSelectSystem(sys)} />
                  <label htmlFor={`sys-${index}`} style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
                      <div>
                        <strong>{sys.robot.brand} {sys.robot.model_name}</strong>
                        <span style={{ marginLeft: 8, fontSize: '0.75rem', padding: '2px 6px', background: 'var(--accent)', borderRadius: 4 }}>{sys.robot.robot_type}</span>
                      </div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        {sys.compatibility.robot_gripper === 'PASS' && <span style={{ color: 'green' }}>[OK]</span>} Greifer
                        {' '}{sys.compatibility.robot_plc === 'PASS' && <span style={{ color: 'green' }}>[OK]</span>} PLC
                      </div>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 6, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 4 }}>
                      <span>Roboter: {sys.robot.brand} {sys.robot.model_name}</span>
                      <span>Greifer: {sys.gripper?.manufacturer} {sys.gripper?.model_name || '—'}</span>
                      <span>PLC: {sys.plc?.brand} {sys.plc?.model_name || '—'}</span>
                      <span>Vision: {sys.vision?.brand} {sys.vision?.model_name || '—'}</span>
                      <span>Sensor: {sys.sensor?.brand} {sys.sensor?.model_name || '—'}</span>
                      <span>Pneumatik: {sys.pneumatic?.brand} {sys.pneumatic?.model_name || '—'}</span>
                      <span>Feeder: {sys.feeder?.brand} {sys.feeder?.model_name || '—'}</span>
                      <span>Sicherheit: {sys.safety_system?.brand} {sys.safety_system?.model_name || '—'}</span>
                      <span>Gehause: {sys.safety_housing?.model_name} ({sys.safety_housing?.width_m}×{sys.safety_housing?.depth_m}m)</span>
                    </div>
                    <div style={{ fontSize: '0.85rem', marginTop: 8, padding: '8px 12px', background: 'rgba(0,0,0,0.05)', borderRadius: 4 }}>
                      <strong>€{sys.total_price.toLocaleString()}</strong> | {sys.delivery_weeks} Wochen Lieferzeit | {sys.operating_angle_deg}° {sys.operating_direction}
                    </div>
                  </label>
                  {index === 0 && <span className="status-indicator status-green" style={{ marginLeft: 8 }}>Empfohlen</span>}
                </div>
              ))}
            </div>
          )}

          {step >= 3 && selectedSystem && (
            <>
              <div className="form-group" style={{ marginTop: 20 }}>
                <label>Projektname</label>
                <input type="text" value={projectName} onChange={(e) => setProjectName(e.target.value)} />
              </div>

              <button className="btn btn-primary" onClick={handleValidate} disabled={!selectedSystem || loading} style={{ marginTop: 16 }}>{loading ? 'Validiere...' : 'Validierung durchführen'}</button>
            </>
          )}
        </div>

        <div className="results-panel card">
          <h2>Live Ergebnisse</h2>
          <div className="gauge">
            <div className="gauge-header">
              <span className="gauge-title">Inertia-Guard</span>
              {result ? <span className={`status-indicator ${result.inertia.status === 'GRÜN' ? 'status-green' : 'status-red'}`}>{result.inertia.status}</span> : <span className="status-indicator status-yellow">WARTEN</span>}
            </div>
            <div className="gauge-value">{result ? `${result.inertia.calculated_inertia} kgm²` : '-- kgm²'}</div>
            <div className="gauge-bar">{result && <div className={`gauge-fill ${getUtilizationColor(result.inertia.utilization_percent)}`} style={{ width: `${result.inertia.utilization_percent}%` }} />}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 4 }}>{result ? `${result.inertia.utilization_percent}% der Nennkapazität` : 'Ausnutzung: --%'}</div>
          </div>

          <div className="gauge">
            <div className="gauge-header"><span className="gauge-title">Cycle-Time-Realist</span></div>
            <div className="gauge-value">{result ? `${result.cycle_time.estimated_seconds}s` : '-- s'}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 4 }}>{result ? result.cycle_time.assumptions[0] : 'inkl. 15% Puffer'}</div>
          </div>

          <div className="interface-check">
            <h3>Interface-Checker</h3>
            {result ? (
              <>
                <div className="check-item"><span className="check-label">Mechanisch</span><span className={`status-indicator ${result.interface.mechanical.status === 'PASS' ? 'status-green' : 'status-red'}`}>{result.interface.mechanical.status}</span></div>
                <div className="check-item"><span className="check-label">Elektrisch</span><span className={`status-indicator ${result.interface.electrical.status === 'PASS' ? 'status-green' : 'status-red'}`}>{result.interface.electrical.status}</span></div>
                <div className="check-item"><span className="check-label">Digital</span><span className={`status-indicator ${result.interface.digital.status === 'PASS' ? 'status-green' : 'status-red'}`}>{result.interface.digital.status}</span></div>
              </>
            ) : <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Warten...</p>}
          </div>

          {tipsForSelection.length > 0 && (
            <div style={{ marginTop: 16, padding: 12, background: 'rgba(234,179,8,0.1)', borderRadius: 4, borderLeft: '3px solid #eab308' }}>
              <h4 style={{ color: '#eab308', marginBottom: 8 }}>Senior Hinweise</h4>
              {tipsForSelection.map((tip, i) => <div key={i} style={{ fontSize: '0.8rem', marginBottom: 4 }}><span className={`status-indicator ${tip.severity === 'WARNING' ? 'status-yellow' : 'status-green'}`} style={{ marginRight: 6 }}>{tip.severity}</span>{tip.tip_text}</div>)}
            </div>
          )}

          {result && selectedSystem && (
            <button className="btn btn-success" style={{ width: '100%', marginTop: 24 }} onClick={handleDownloadReport}>
              Technisches_Audit_{projectName}.pdf herunterladen
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function SeniorPortal() {
  const [tips, setTips] = useState<KnowledgeTip[]>([]);
  const [license, setLicense] = useState<{ total: number; used: number } | null>(null);
  const [robots, setRobots] = useState<Robot[]>([]);
  const [grippers, setGrippers] = useState<Gripper[]>([]);
  const [newTip, setNewTip] = useState({ target_type: 'robot', target_id: '', severity: 'INFO', tip_text: '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    const [t, l, r, g] = await Promise.all([getKnowledgeTips(), getLicense(), getAllRobots(), getAllGrippers()]);
    setTips(t); setLicense(l); setRobots(r); setGrippers(g);
  };

  const handleAddTip = async () => {
    if (!newTip.target_id || !newTip.tip_text) return;
    setSaving(true);
    try {
      await addKnowledgeTip(newTip.target_type, newTip.target_id, newTip.severity, newTip.tip_text);
      setNewTip({ target_type: 'robot', target_id: '', severity: 'INFO', tip_text: '' });
      await loadData();
    } catch (e) { console.error(e); } finally { setSaving(false); }
  };

  const handleDeleteTip = async (tipId: number) => { await deleteKnowledgeTip(tipId); await loadData(); };
  const remaining = license ? license.total - license.used : 0;

  return (
    <div className="container">
      <h2 style={{ marginBottom: 24 }}>Senior Portal</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 24, marginBottom: 32 }}>
        <div className="card">
          <h3>Lizenz Status</h3>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: remaining < 5 ? 'var(--accent-red)' : 'var(--accent-green)' }}>{remaining} / {license?.total || 25}</div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Verbleibende Audits</p>
        </div>
        <div className="card">
          <h3>Neuen Hinweis hinzufügen</h3>
          <div className="form-group">
            <label>Typ</label>
            <select value={newTip.target_type} onChange={(e) => setNewTip({ ...newTip, target_type: e.target.value, target_id: '' })}>
              <option value="robot">Robot</option><option value="gripper">Greifer</option><option value="all">Alle</option>
            </select>
          </div>
          <div className="form-group">
            <label>Komponente</label>
            <select value={newTip.target_id} onChange={(e) => setNewTip({ ...newTip, target_id: e.target.value })}>
              <option value="">-- Auswählen --</option>
              {newTip.target_type === 'robot' && robots.map(r => <option key={r.id} value={r.id}>{r.brand} {r.model_name}</option>)}
              {newTip.target_type === 'gripper' && grippers.map(g => <option key={g.id} value={g.id}>{g.manufacturer} {g.model_name}</option>)}
              {newTip.target_type === 'all' && <option value="all">Alle Komponenten</option>}
            </select>
          </div>
          <div className="form-group">
            <label>Schweregrad</label>
            <select value={newTip.severity} onChange={(e) => setNewTip({ ...newTip, severity: e.target.value })}>
              <option value="INFO">INFO</option><option value="WARNING">WARNING</option>
            </select>
          </div>
          <div className="form-group">
            <label>Hinweis</label>
            <textarea value={newTip.tip_text} onChange={(e) => setNewTip({ ...newTip, tip_text: e.target.value })} style={{ width: '100%', minHeight: 60, padding: 8, background: 'var(--bg-tertiary)', border: '1px solid var(--border-color)', color: 'var(--text-primary)' }} />
          </div>
          <button className="btn btn-primary" onClick={handleAddTip} disabled={saving || !newTip.target_id || !newTip.tip_text}>{saving ? 'Speichere...' : 'Hinzufügen'}</button>
        </div>
      </div>
      <div className="card">
        <h3>Wissens-Datenbank</h3>
        {tips.length === 0 ? <p style={{ color: 'var(--text-secondary)' }}>Keine Hinweise.</p> : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead><tr style={{ borderBottom: '1px solid var(--border-color)' }}><th style={{ textAlign: 'left', padding: 8 }}>ID</th><th style={{ textAlign: 'left', padding: 8 }}>Typ</th><th style={{ textAlign: 'left', padding: 8 }}>Für</th><th style={{ textAlign: 'left', padding: 8 }}>Grad</th><th style={{ textAlign: 'left', padding: 8 }}>Hinweis</th><th style={{ textAlign: 'right', padding: 8 }}>Aktion</th></tr></thead>
            <tbody>{tips.map(tip => (
              <tr key={tip.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: 8 }}>{tip.id}</td><td style={{ padding: 8 }}>{tip.target_type}</td><td style={{ padding: 8 }}>{tip.target_id}</td>
                <td style={{ padding: 8 }}><span className={`status-indicator ${tip.severity === 'WARNING' ? 'status-yellow' : 'status-green'}`}>{tip.severity}</span></td>
                <td style={{ padding: 8, maxWidth: 300 }}>{tip.tip_text}</td>
                <td style={{ padding: 8, textAlign: 'right' }}><button className="btn btn-danger" style={{ padding: '4px 8px', fontSize: '0.75rem' }} onClick={() => handleDeleteTip(tip.id)}>Löschen</button></td>
              </tr>
            ))}</tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export { JuniorDashboard, SeniorPortal };