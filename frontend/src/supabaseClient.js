import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://vrarewawdduczgdsxlkh.supabase.co'
const supabaseKey = 'sb_publishable_EzrIrDqmVmL2pmEbvyntAQ_T_4vWtZN'

const supabase = createClient(supabaseUrl, supabaseKey)

export default supabase