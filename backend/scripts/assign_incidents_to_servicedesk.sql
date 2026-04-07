-- Assign all open incidents to the Servicedesk support group
-- Run this with: psql -U opsit -d opsit_db -f assign_incidents_to_servicedesk.sql

-- First, find the Servicedesk support group ID
DO $$
DECLARE
    v_servicedesk_id UUID;
    v_incident_count INTEGER;
BEGIN
    -- Get Servicedesk group ID
    SELECT id INTO v_servicedesk_id
    FROM support_groups
    WHERE name = 'Servicedesk'
      AND is_deleted = FALSE
    LIMIT 1;

    IF v_servicedesk_id IS NULL THEN
        RAISE EXCEPTION 'Servicedesk support group not found!';
    END IF;

    RAISE NOTICE 'Found Servicedesk group with ID: %', v_servicedesk_id;

    -- Count incidents to be updated
    SELECT COUNT(*) INTO v_incident_count
    FROM incidents
    WHERE status IN ('new', 'assigned', 'in_progress', 'pending')
      AND assigned_group_id IS NULL
      AND is_deleted = FALSE;

    RAISE NOTICE 'Found % open incident(s) without assigned group', v_incident_count;

    IF v_incident_count = 0 THEN
        RAISE NOTICE 'No incidents to update.';
        RETURN;
    END IF;

    -- Update incidents
    UPDATE incidents
    SET assigned_group_id = v_servicedesk_id,
        status = CASE
            WHEN status = 'new' THEN 'assigned'
            ELSE status
        END,
        updated_at = NOW()
    WHERE status IN ('new', 'assigned', 'in_progress', 'pending')
      AND assigned_group_id IS NULL
      AND is_deleted = FALSE;

    RAISE NOTICE 'Successfully assigned % incident(s) to Servicedesk support group!', v_incident_count;
    RAISE NOTICE 'Incidents with status "new" have been updated to "assigned".';
END $$;
