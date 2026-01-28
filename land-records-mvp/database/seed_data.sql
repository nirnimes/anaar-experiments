-- Seed data for Delhi Land Records MVP
-- Sample properties for Greater Kailash (I, II, III) and Chitranjan Park

-- Greater Kailash I properties
INSERT INTO properties (plot_number, locality, khasra_number, area_sqm, owner_name, registration_date, last_transaction_date, encumbrance_status, property_type, market_value_estimate, data_source, last_verified)
VALUES
('A-123', 'Greater Kailash I', '567/12', 350.5, 'Anonymous', '2015-03-15', '2022-08-20', 'Clear', 'Residential', 25000000, 'Manual Entry', '2026-01-27'),
('C-92', 'Greater Kailash I', '678/3', 400.0, 'Anonymous', '2012-11-18', '2021-07-22', 'Clear', 'Residential', 32000000, 'Public Listing', '2026-01-26'),
('M-45', 'Greater Kailash I', '789/15', 300.0, 'Anonymous', '2018-05-10', '2023-02-14', 'Clear', 'Residential', 22000000, 'Crowdsourced', '2026-01-25'),
('N-67', 'Greater Kailash I', '890/8', 450.0, 'Anonymous', '2010-09-05', '2020-12-30', 'Mortgaged', 'Residential', 35000000, 'Manual Portal Query', '2026-01-24'),
('E-34', 'Greater Kailash I', '234/20', 280.0, 'Anonymous', '2016-07-22', '2024-06-15', 'Clear', 'Residential', 20000000, 'Public Listing', '2026-01-27');

-- Greater Kailash II properties
INSERT INTO properties (plot_number, locality, khasra_number, area_sqm, owner_name, registration_date, last_transaction_date, encumbrance_status, property_type, market_value_estimate, data_source, last_verified)
VALUES
('M-45', 'Greater Kailash II', '234/8', 500.0, 'Anonymous', '2010-06-12', '2020-11-05', 'Mortgaged', 'Residential', 40000000, 'Public Listing', '2026-01-25'),
('K-78', 'Greater Kailash II', '456/9', 600.0, 'Anonymous', '2008-03-20', '2019-09-12', 'Clear', 'Residential', 48000000, 'Manual Entry', '2026-01-26'),
('R-156', 'Greater Kailash II', '567/14', 550.0, 'Anonymous', '2013-12-05', '2022-04-18', 'Clear', 'Residential', 45000000, 'Crowdsourced', '2026-01-25'),
('T-89', 'Greater Kailash II', '678/22', 400.0, 'Anonymous', '2017-08-15', '2023-11-20', 'Disputed', 'Residential', 35000000, 'Manual Portal Query', '2026-01-24'),
('W-234', 'Greater Kailash II', '789/5', 700.0, 'Anonymous', '2005-01-10', '2018-07-25', 'Mortgaged', 'Residential', 58000000, 'Public Listing', '2026-01-23');

-- Greater Kailash III properties
INSERT INTO properties (plot_number, locality, khasra_number, area_sqm, owner_name, registration_date, last_transaction_date, encumbrance_status, property_type, market_value_estimate, data_source, last_verified)
VALUES
('S-156', 'Greater Kailash III', '445/20', 600.0, 'Anonymous', '2005-02-28', '2023-04-15', 'Disputed', 'Commercial', 60000000, 'Manual Portal Query', '2026-01-27'),
('L-92', 'Greater Kailash III', '556/12', 800.0, 'Anonymous', '2000-11-30', '2017-05-22', 'Clear', 'Commercial', 85000000, 'Manual Entry', '2026-01-26'),
('P-45', 'Greater Kailash III', '667/8', 350.0, 'Anonymous', '2019-06-18', '2024-01-10', 'Clear', 'Residential', 30000000, 'Public Listing', '2026-01-27'),
('Q-123', 'Greater Kailash III', '778/15', 450.0, 'Anonymous', '2014-03-12', '2021-08-30', 'Mortgaged', 'Residential', 38000000, 'Crowdsourced', '2026-01-25'),
('D-89', 'Greater Kailash III', '889/25', 550.0, 'Anonymous', '2011-09-08', '2022-12-05', 'Clear', 'Mixed-use', 50000000, 'Manual Portal Query', '2026-01-24');

-- Chitranjan Park properties
INSERT INTO properties (plot_number, locality, khasra_number, area_sqm, owner_name, registration_date, last_transaction_date, encumbrance_status, property_type, market_value_estimate, data_source, last_verified)
VALUES
('F-78', 'Chitranjan Park', '891/5', 250.0, 'Anonymous', '2018-09-30', '2018-09-30', 'Clear', 'Residential', 18000000, 'Crowdsourced', '2026-01-20'),
('H-45', 'Chitranjan Park', '912/8', 300.0, 'Anonymous', '2015-04-15', '2022-06-20', 'Clear', 'Residential', 22000000, 'Public Listing', '2026-01-27'),
('J-123', 'Chitranjan Park', '923/12', 280.0, 'Anonymous', '2017-11-22', '2023-03-15', 'Mortgaged', 'Residential', 20000000, 'Manual Entry', '2026-01-26'),
('K-67', 'Chitranjan Park', '934/18', 350.0, 'Anonymous', '2012-07-08', '2020-10-25', 'Clear', 'Residential', 25000000, 'Crowdsourced', '2026-01-25'),
('L-234', 'Chitranjan Park', '945/22', 400.0, 'Anonymous', '2009-02-14', '2019-12-30', 'Clear', 'Residential', 28000000, 'Manual Portal Query', '2026-01-24'),
('M-89', 'Chitranjan Park', '956/5', 220.0, 'Anonymous', '2020-05-18', '2024-08-12', 'Clear', 'Residential', 16000000, 'Public Listing', '2026-01-27'),
('N-156', 'Chitranjan Park', '967/9', 320.0, 'Anonymous', '2016-10-25', '2023-07-05', 'Disputed', 'Residential', 23000000, 'Manual Entry', '2026-01-23'),
('P-78', 'Chitranjan Park', '978/15', 270.0, 'Anonymous', '2013-01-30', '2021-11-18', 'Clear', 'Residential', 19500000, 'Crowdsourced', '2026-01-26');

-- Additional diverse properties for better testing
INSERT INTO properties (plot_number, locality, khasra_number, area_sqm, owner_name, registration_date, last_transaction_date, encumbrance_status, property_type, market_value_estimate, data_source, last_verified)
VALUES
('X-999', 'Greater Kailash I', '999/99', 1200.0, 'Anonymous', '2002-05-15', '2015-03-20', 'Clear', 'Commercial', 150000000, 'Manual Portal Query', '2026-01-20'),
('Y-888', 'Greater Kailash II', '888/88', 150.0, 'Anonymous', '2021-08-10', '2024-12-01', 'Clear', 'Residential', 12000000, 'Crowdsourced', '2026-01-27'),
('Z-777', 'Chitranjan Park', '777/77', 180.0, 'Anonymous', '2022-03-25', '2024-11-15', 'Clear', 'Residential', 13500000, 'Public Listing', '2026-01-27');
