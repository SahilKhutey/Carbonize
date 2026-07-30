-- Inquiries table
CREATE TABLE IF NOT EXISTS inquiries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  email text NOT NULL,
  company text,
  industry text,
  capacity text,
  timeline text,
  message text,
  source text DEFAULT 'landing_page',
  created_at timestamp with time zone DEFAULT now()
);

-- New table for ROI calculator submissions
CREATE TABLE IF NOT EXISTS roi_calculations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  capacity numeric NOT NULL,
  opex numeric NOT NULL,
  energy numeric NOT NULL,
  annual_savings numeric NOT NULL,
  ten_year_npv numeric NOT NULL,
  payback_months numeric NOT NULL,
  email text,
  created_at timestamp with time zone DEFAULT now()
);

-- Indexes for analytics
CREATE INDEX IF NOT EXISTS idx_inquiries_created_at ON inquiries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_inquiries_source ON inquiries(source);
CREATE INDEX IF NOT EXISTS idx_roi_created_at ON roi_calculations(created_at DESC);

-- Row Level Security
ALTER TABLE inquiries ENABLE ROW LEVEL SECURITY;
ALTER TABLE roi_calculations ENABLE ROW LEVEL SECURITY;

-- Allow public insert (for forms)
CREATE POLICY "Public insert on inquiries" ON inquiries
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Public insert on roi_calculations" ON roi_calculations
  FOR INSERT WITH CHECK (true);

-- Only authenticated users can read
CREATE POLICY "Authenticated read on inquiries" ON inquiries
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated read on roi_calculations" ON roi_calculations
  FOR SELECT USING (auth.role() = 'authenticated');
