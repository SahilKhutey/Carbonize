import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Play, Users, AlertTriangle, Trophy, Clock } from 'lucide-react';
import { gamedayApi } from '@/gameday/api';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

export function GameDayDashboard() {
  const [selectedGameday, setSelectedGameday] = useState<string | null>('gd_2024_q1_001');
  const [playerName, setPlayerName] = useState('Alice Chen');
  
  const { data: gamedays = [
    {
      id: 'gd_2024_q1_001',
      name: 'Q1 2024 — Database Failover Drill',
      date: '2024-03-15',
      duration_minutes: 120,
      participants: 4,
      injects: 2,
    },
    {
      id: 'gd_2024_q1_002',
      name: 'Q1 2024 — Kafka Broker Failure',
      date: '2024-03-22',
      duration_minutes: 90,
      participants: 3,
      injects: 1,
    },
  ] } = useQuery({
    queryKey: ['gamedays'],
    queryFn: gamedayApi.list,
  });
  
  const { data: status } = useQuery({
    queryKey: ['gameday-status', selectedGameday],
    queryFn: () => gamedayApi.getStatus(selectedGameday!),
    enabled: !!selectedGameday,
    refetchInterval: 3000,
  });
  
  const startMutation = useMutation({
    mutationFn: (id: string) => gamedayApi.run(id),
    onSuccess: () => toast.success('Game Day exercise started!'),
  });
  
  const recordAction = useMutation({
    mutationFn: (action: any) => gamedayApi.recordAction(selectedGameday!, action),
    onSuccess: () => toast.success('Action recorded to scoreboard!'),
  });
  
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text flex items-center gap-2">
            <Trophy className="w-7 h-7 text-primary-500" />
            Game Days Platform
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            Scheduled chaos exercises with multi-team incident simulation & scoring
          </p>
        </div>
      </div>
      
      {/* ─── Game day list ─────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {gamedays.map((gd: any) => (
          <div
            key={gd.id}
            className={cn(
              'bg-surface border border-border rounded-theme-md p-4 transition-colors',
              selectedGameday === gd.id && 'border-primary-500 ring-1 ring-primary-500',
            )}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-semibold text-text">{gd.name}</h3>
                <p className="text-xs text-text-tertiary mt-1">Date: {gd.date}</p>
              </div>
              <span className="text-xs px-2 py-1 bg-primary-500/20 text-primary-400 rounded-full font-mono">
                {gd.duration_minutes} min
              </span>
            </div>
            
            <div className="grid grid-cols-3 gap-2 text-xs mb-3">
              <div className="bg-surface-elevated rounded-theme-md p-2 text-center">
                <Users className="w-4 h-4 mx-auto text-sky-400 mb-1" />
                <div className="text-text font-mono font-bold">{gd.participants}</div>
              </div>
              <div className="bg-surface-elevated rounded-theme-md p-2 text-center">
                <AlertTriangle className="w-4 h-4 mx-auto text-warning mb-1" />
                <div className="text-text font-mono font-bold">{gd.injects}</div>
              </div>
              <div className="bg-surface-elevated rounded-theme-md p-2 text-center">
                <Clock className="w-4 h-4 mx-auto text-success mb-1" />
                <div className="text-text font-mono font-bold">{gd.duration_minutes}m</div>
              </div>
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedGameday(gd.id)}
                className="theme-button flex-1 text-xs"
              >
                Select Scenario
              </button>
              <button
                onClick={() => startMutation.mutate(gd.id)}
                className="theme-button-primary text-xs"
              >
                <Play className="w-3 h-3 inline mr-1" />
                Start Simulation
              </button>
            </div>
          </div>
        ))}
      </div>
      
      {/* ─── Live game day console ───────────────────────────────── */}
      <div className="bg-surface border border-border rounded-theme-md p-4">
        <h3 className="text-lg font-semibold text-text mb-3">Incident Simulation Console</h3>
        <div className="grid grid-cols-4 gap-3 mb-4">
          <StatBox label="Current Phase" value={status?.current_phase || 'detection'} />
          <StatBox label="Inject Progress" value={`${status?.injects_completed || 1}/${status?.injects_total || 2}`} />
          <StatBox label="Leaderboard Score" value="88.5/100" />
          <StatBox label="Elapsed Time" value="14m" />
        </div>
        
        {/* ─── Action buttons ─────────────────────────────────────── */}
        <div className="space-y-3">
          <div className="text-xs text-text-tertiary uppercase font-semibold">Record Participant Incident Actions</div>
          <div className="grid grid-cols-4 gap-2">
            <ActionButton
              label="Detect Issue"
              color="sky"
              onClick={() =>
                recordAction.mutate({
                  participant_id: playerName,
                  action_type: 'detection',
                  time_to_detect_seconds: 45,
                  description: 'Identified high latency in db pool',
                })
              }
            />
            <ActionButton
              label="Mitigate Issue"
              color="warning"
              onClick={() =>
                recordAction.mutate({
                  participant_id: playerName,
                  action_type: 'mitigation',
                  quality: 90,
                  description: 'Triggered failover to secondary replica',
                })
              }
            />
            <ActionButton
              label="Resolve Incident"
              color="success"
              onClick={() =>
                recordAction.mutate({
                  participant_id: playerName,
                  action_type: 'resolution',
                  verified: true,
                  description: 'Confirmed health checks green',
                })
              }
            />
            <ActionButton
              label="Send Update"
              color="info"
              onClick={() =>
                recordAction.mutate({
                  participant_id: playerName,
                  action_type: 'communication',
                  description: 'Broadcast status update on Slack',
                })
              }
            />
          </div>
          
          <input
            type="text"
            placeholder="Participant Name"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            className="w-full bg-surface-elevated border border-border rounded-theme-md px-3 py-2 text-text text-xs font-mono"
          />
        </div>
      </div>
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-surface-elevated rounded-theme-md p-3">
      <div className="text-xs text-text-tertiary uppercase">{label}</div>
      <div className="text-lg font-bold text-text font-mono mt-1">{value}</div>
    </div>
  );
}

function ActionButton({ label, color, onClick }: any) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'px-3 py-2 rounded-theme-md text-xs font-medium transition-colors',
        color === 'sky' && 'bg-sky-500/20 text-sky-400 hover:bg-sky-500/30',
        color === 'warning' && 'bg-warning/20 text-warning hover:bg-warning/30',
        color === 'success' && 'bg-success/20 text-success hover:bg-success/30',
        color === 'info' && 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30',
      )}
    >
      {label}
    </button>
  );
}
