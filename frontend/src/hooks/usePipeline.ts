import { useState, useCallback } from 'react';

export type PipelineStage = 'busca' | 'normalizacao' | 'precificacao' | 'roi' | 'ranking';

export interface PipelineStep {
  id: PipelineStage;
  label: string;
  status: 'pending' | 'active' | 'done' | 'error';
}

const INITIAL_STEPS: PipelineStep[] = [
  { id: 'busca', label: 'Busca', status: 'pending' },
  { id: 'normalizacao', label: 'Normalização', status: 'pending' },
  { id: 'precificacao', label: 'Precificação', status: 'pending' },
  { id: 'roi', label: 'ROI', status: 'pending' },
  { id: 'ranking', label: 'Ranking', status: 'pending' },
];

export function usePipeline() {
  const [steps, setSteps] = useState<PipelineStep[]>(INITIAL_STEPS);
  const [isActive, setIsActive] = useState(false);

  const startPipeline = useCallback(async () => {
    setIsActive(true);
    setSteps(INITIAL_STEPS);

    for (let i = 0; i < INITIAL_STEPS.length; i++) {
      // Set current to active
      setSteps(prev => prev.map((s, idx) => 
        idx === i ? { ...s, status: 'active' } : s
      ));

      // Mock processing time per stage
      const delay = Math.random() * 800 + 400; // 400ms to 1200ms
      await new Promise(r => setTimeout(r, delay));

      // Set current to done
      setSteps(prev => prev.map((s, idx) => 
        idx === i ? { ...s, status: 'done' } : s
      ));
    }

    setIsActive(false);
  }, []);

  const resetPipeline = useCallback(() => {
    setSteps(INITIAL_STEPS);
    setIsActive(false);
  }, []);

  return {
    steps,
    isActive,
    startPipeline,
    resetPipeline
  };
}
