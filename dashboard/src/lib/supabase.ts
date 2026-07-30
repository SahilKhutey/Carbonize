import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://placeholder.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'placeholder-key';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// ─── Types ────────────────────────────────────────────────────
export interface Inquiry {
  id?: string;
  name: string;
  email: string;
  company?: string;
  industry?: string;
  capacity?: string;
  timeline?: string;
  message?: string;
  source?: string;
  created_at?: string;
}

// ─── Submit inquiry ───────────────────────────────────────────
export async function submitInquiry(inquiry: Inquiry): Promise<{ success: boolean; error?: string }> {
  try {
    const { data, error } = await supabase
      .from('inquiries')
      .insert([inquiry])
      .select();

    if (error) {
      console.error('Supabase error:', error);
      return { success: false, error: error.message };
    }

    return { success: true };
  } catch (err) {
    console.error('Submit error:', err);
    return { success: false, error: err instanceof Error ? err.message : 'Unknown error' };
  }
}

// ─── Track ROI calculator submission ─────────────────────────
export interface ROIResult {
  capacity: number;
  opex: number;
  energy: number;
  annual_savings: number;
  ten_year_npv: number;
  payback_months: number;
  email?: string;
}

export async function trackROIResult(result: ROIResult): Promise<void> {
  try {
    await supabase.from('roi_calculations').insert([result]);
  } catch (err) {
    console.error('ROI tracking error:', err);
  }
}
