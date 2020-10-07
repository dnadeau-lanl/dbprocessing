CREATE DATABASE sndd;
CREATE TABLE mission (
	mission_id INTEGER NOT NULL, 
	mission_name VARCHAR(20) NOT NULL, 
	rootdir VARCHAR(50) NOT NULL, 
	incoming_dir VARCHAR(50) NOT NULL, 
	codedir VARCHAR(50), 
	inspectordir VARCHAR(50), 
	errordir VARCHAR(50), 
	PRIMARY KEY (mission_id), 
	UNIQUE (mission_name)
);
INSERT INTO mission VALUES(1,'testDB','.','incoming','','',NULL);
CREATE TABLE logging (
	logging_id INTEGER NOT NULL, 
	currently_processing BOOLEAN NOT NULL, 
	pid INTEGER, 
	processing_start_time DATETIME NOT NULL, 
	processing_end_time DATETIME, 
	comment TEXT, 
	mission_id INTEGER NOT NULL, 
	user VARCHAR(30) NOT NULL, 
	hostname VARCHAR(100) NOT NULL, 
	PRIMARY KEY (logging_id), 
	CHECK (processing_start_time < processing_end_time), 
	CHECK (currently_processing IN (0, 1)), 
	FOREIGN KEY(mission_id) REFERENCES mission (mission_id)
);
INSERT INTO logging VALUES(1,0,23567,'2018-05-11 23:29:31.185263',NULL,'Nominal Exit:NMC_1',1,'myles','myles-XPS13-9333');
INSERT INTO logging VALUES(2,0,23568,'2018-05-11 23:29:31.834107',NULL,'Nominal Exit:NMC_1',1,'myles','myles-XPS13-9333');
CREATE TABLE satellite (
	satellite_id INTEGER NOT NULL, 
	satellite_name VARCHAR(20) NOT NULL, 
	mission_id INTEGER NOT NULL, 
	PRIMARY KEY (satellite_id), 
	CONSTRAINT unique_pairs_satellite UNIQUE (satellite_name, mission_id), 
	FOREIGN KEY(mission_id) REFERENCES mission (mission_id)
);
INSERT INTO satellite VALUES(1,'testDB-a',1);
CREATE TABLE instrument (
	instrument_id INTEGER NOT NULL, 
	instrument_name VARCHAR(20) NOT NULL, 
	satellite_id INTEGER NOT NULL, 
	PRIMARY KEY (instrument_id), 
	CONSTRAINT unique_pairs_instrument UNIQUE (instrument_name, satellite_id), 
	FOREIGN KEY(satellite_id) REFERENCES satellite (satellite_id)
);
INSERT INTO instrument VALUES(1,'rot13',1);
CREATE TABLE product (
	product_id INTEGER NOT NULL, 
	product_name VARCHAR(100) NOT NULL, 
	instrument_id INTEGER NOT NULL, 
	relative_path VARCHAR(100) NOT NULL, 
	level FLOAT NOT NULL, 
	format TEXT NOT NULL, 
	product_description TEXT, 
	PRIMARY KEY (product_id), 
	CONSTRAINT unique_triplet_product UNIQUE (product_name, instrument_id, relative_path), 
	FOREIGN KEY(instrument_id) REFERENCES instrument (instrument_id)
);
INSERT INTO product VALUES(1,'testDB_rot13_L1',1,'L1',1.0,'testDB_{datetime}.cat','');
INSERT INTO product VALUES(2,'testDB_rot13_L0_second',1,'L0',0.0,'testDB_001_{nnn}.raw','');
INSERT INTO product VALUES(3,'testDB_rot13_L2',1,'L2',2.0,'testDB_{datetime}.rot','');
INSERT INTO product VALUES(4,'testDB_rot13_L0_first',1,'L0',0.0,'testDB_000_{nnn}.raw','');
CREATE TABLE file (
	file_id INTEGER NOT NULL, 
	filename VARCHAR(250) NOT NULL, 
	utc_file_date DATE, 
	utc_start_time DATETIME, 
	utc_stop_time DATETIME, 
	data_level FLOAT NOT NULL, 
	interface_version SMALLINT NOT NULL, 
	quality_version SMALLINT NOT NULL, 
	revision_version SMALLINT NOT NULL, 
	verbose_provenance TEXT, 
	check_date DATETIME, 
	quality_comment TEXT, 
	caveats TEXT, 
	file_create_date DATETIME NOT NULL, 
	met_start_time FLOAT, 
	met_stop_time FLOAT, 
	exists_on_disk BOOLEAN NOT NULL, 
	quality_checked BOOLEAN, 
	product_id INTEGER NOT NULL, 
	shasum VARCHAR(40), 
	process_keywords TEXT, 
	PRIMARY KEY (file_id), 
	CHECK (utc_stop_time is not NULL OR met_stop_time is not NULL), 
	CHECK (utc_start_time is not NULL OR met_start_time is not NULL), 
	CHECK (met_start_time <= met_stop_time), 
	CHECK (utc_start_time <= utc_stop_time), 
	CHECK (interface_version >= 1), 
	CONSTRAINT "Unique file tuple" UNIQUE (utc_file_date, product_id, interface_version, quality_comment, revision_version), 
	CHECK (exists_on_disk IN (0, 1)), 
	CHECK (quality_checked IN (0, 1)), 
	FOREIGN KEY(product_id) REFERENCES product (product_id)
);
INSERT INTO file VALUES(1,'testDB_001_001.raw','2016-01-02','2016-01-02 00:00:00.000000','2016-01-03 00:00:00.000000',0.0,1,0,0,NULL,NULL,NULL,NULL,'2018-05-11 19:29:29.551336',NULL,NULL,1,NULL,2,'50d9e084598d5510ebe88b52ab69e75935d5820b','nnn=001');
INSERT INTO file VALUES(2,'testDB_001_000.raw','2016-01-01','2016-01-01 00:00:00.000000','2016-01-02 00:00:00.000000',0.0,1,0,0,NULL,NULL,NULL,NULL,'2018-05-11 19:29:29.551336',NULL,NULL,1,NULL,2,'edd69d888d7d7ea0177ea73a2d4e56546fe36e50','nnn=001');
INSERT INTO file VALUES(3,'testDB_000_003.raw','2016-01-04','2016-01-04 00:00:00.000000','2016-01-05 00:00:00.000000',0.0,1,0,0,NULL,NULL,NULL,NULL,'2018-05-11 19:29:29.551336',NULL,NULL,1,NULL,4,'6300b792c6018b559b992aa469bc2c45d500be8f','nnn=000');
INSERT INTO file VALUES(4,'testDB_000_002.raw','2016-01-03','2016-01-03 00:00:00.000000','2016-01-04 00:00:00.000000',0.0,1,0,0,NULL,NULL,NULL,NULL,'2018-05-11 19:29:29.551336',NULL,NULL,1,NULL,4,'73218113cb5336e92f721898c11a606bb22e0e7a','nnn=000');
INSERT INTO file VALUES(5,'testDB_000_001.raw','2016-01-02','2016-01-02 00:00:00.000000','2016-01-03 00:00:00.000000',0.0,1,0,0,NULL,NULL,NULL,NULL,'2018-05-11 19:29:29.551336',NULL,NULL,1,NULL,4,'1519b777236c5044a9b90b27c0071a259dfa3076','nnn=000');
INSERT INTO file VALUES(6,'testDB_000_000.raw','2016-01-01','2016-01-01 00:00:00.000000','2016-01-02 00:00:00.000000',0.0,1,0,0,NULL,NULL,NULL,NULL,'2018-05-11 19:29:29.551336',NULL,NULL,1,NULL,4,'f84f7ab0c6949d17ee6a7a02564fd4985bc97be5','nnn=000');
INSERT INTO file VALUES(7,'testDB_2016-01-01.cat','2016-01-01','2016-01-01 00:00:00.000000','2016-01-02 00:00:00.000000',1.0,1,0,0,'/home/myles/Work/dbprocessing/functional_test/scripts/run_rot13_L0toL1.py /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_000.raw /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_001.raw /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_002.raw /tmp/tmpZFfI3j_testDB_2016-01-01.cat_runMe/testDB_2016-01-01.cat',NULL,NULL,NULL,'2018-05-11 19:29:32.295367',NULL,NULL,1,NULL,1,'1fa0f7f9b896e7801d16849b40e2ccc09ff9f275','nnn=2016-01-01');
INSERT INTO file VALUES(8,'testDB_2016-01-02.cat','2016-01-02','2016-01-02 00:00:00.000000','2016-01-03 00:00:00.000000',1.0,1,0,0,'/home/myles/Work/dbprocessing/functional_test/scripts/run_rot13_L0toL1.py /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_000.raw /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_001.raw /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_002.raw /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_003.raw /tmp/tmpTRQAqL_testDB_2016-01-02.cat_runMe/testDB_2016-01-02.cat',NULL,NULL,NULL,'2018-05-11 19:29:33.419379',NULL,NULL,1,NULL,1,'f62bb936aad87d8c1781ee86fbccfac7bed9a099','nnn=2016-01-02');
INSERT INTO file VALUES(9,'testDB_2016-01-03.cat','2016-01-03','2016-01-03 00:00:00.000000','2016-01-04 00:00:00.000000',1.0,1,0,0,'/home/myles/Work/dbprocessing/functional_test/scripts/run_rot13_L0toL1.py /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_000.raw /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_001.raw /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_002.raw /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_003.raw /tmp/tmpLkHJ46_testDB_2016-01-03.cat_runMe/testDB_2016-01-03.cat',NULL,NULL,NULL,'2018-05-11 19:29:34.547392',NULL,NULL,1,NULL,1,'f62bb936aad87d8c1781ee86fbccfac7bed9a099','nnn=2016-01-03');
INSERT INTO file VALUES(10,'testDB_2016-01-04.cat','2016-01-04','2016-01-04 00:00:00.000000','2016-01-05 00:00:00.000000',1.0,1,0,0,'/home/myles/Work/dbprocessing/functional_test/scripts/run_rot13_L0toL1.py /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_001.raw /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_002.raw /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_003.raw /tmp/tmpZplnNa_testDB_2016-01-04.cat_runMe/testDB_2016-01-04.cat',NULL,NULL,NULL,'2018-05-11 19:29:35.639404',NULL,NULL,1,NULL,1,'e116d9860587fb4aa9a1438385792aa3891b4258','nnn=2016-01-04');
INSERT INTO file VALUES(11,'testDB_2016-01-05.cat','2016-01-05','2016-01-05 00:00:00.000000','2016-01-06 00:00:00.000000',1.0,1,0,0,'/home/myles/Work/dbprocessing/functional_test/scripts/run_rot13_L0toL1.py /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_002.raw /home/myles/Work/dbprocessing/functional_test/L0/testDB_000_003.raw /tmp/tmp53BIEn_testDB_2016-01-05.cat_runMe/testDB_2016-01-05.cat',NULL,NULL,NULL,'2018-05-11 19:29:36.739417',NULL,NULL,1,NULL,1,'f4511f742ea9e735c113c93183c1e94b90281221','nnn=2016-01-05');
INSERT INTO file VALUES(12,'testDB_2016-01-01.rot','2016-01-01','2016-01-01 00:00:00.000000','2016-01-02 00:00:00.000000',2.0,1,0,0,'/home/myles/Work/dbprocessing/functional_test/scripts/run_rot13_L1toL2.py /home/myles/Work/dbprocessing/functional_test/L1/testDB_2016-01-01.cat /tmp/tmp1MPVTg_testDB_2016-01-01.rot_runMe/testDB_2016-01-01.rot',NULL,NULL,NULL,'2018-05-11 19:29:38.079432',NULL,NULL,1,NULL,3,'3f866f3a702d2029e44f533c1dc01bf431fe05bc',NULL);
INSERT INTO file VALUES(13,'testDB_2016-01-02.rot','2016-01-02','2016-01-02 00:00:00.000000','2016-01-03 00:00:00.000000',2.0,1,0,0,'/home/myles/Work/dbprocessing/functional_test/scripts/run_rot13_L1toL2.py /home/myles/Work/dbprocessing/functional_test/L1/testDB_2016-01-02.cat /tmp/tmpA8QjRn_testDB_2016-01-02.rot_runMe/testDB_2016-01-02.rot',NULL,NULL,NULL,'2018-05-11 19:29:39.151443',NULL,NULL,1,NULL,3,'e8590f08a3dd2ba2a812f1c3855c0cc8bd738a2d',NULL);
INSERT INTO file VALUES(14,'testDB_2016-01-03.rot','2016-01-03','2016-01-03 00:00:00.000000','2016-01-04 00:00:00.000000',2.0,1,0,0,'/home/myles/Work/dbprocessing/functional_test/scripts/run_rot13_L1toL2.py /home/myles/Work/dbprocessing/functional_test/L1/testDB_2016-01-03.cat /tmp/tmpwsz0v8_testDB_2016-01-03.rot_runMe/testDB_2016-01-03.rot',NULL,NULL,NULL,'2018-05-11 19:29:40.235456',NULL,NULL,1,NULL,3,'e8590f08a3dd2ba2a812f1c3855c0cc8bd738a2d',NULL);
INSERT INTO file VALUES(15,'testDB_2016-01-04.rot','2016-01-04','2016-01-04 00:00:00.000000','2016-01-05 00:00:00.000000',2.0,1,0,0,'/home/myles/Work/dbprocessing/functional_test/scripts/run_rot13_L1toL2.py /home/myles/Work/dbprocessing/functional_test/L1/testDB_2016-01-04.cat /tmp/tmpdBevCO_testDB_2016-01-04.rot_runMe/testDB_2016-01-04.rot',NULL,NULL,NULL,'2018-05-11 19:29:41.335468',NULL,NULL,1,NULL,3,'2ead5876ab825848b976d21220531793929bdc89',NULL);
INSERT INTO file VALUES(16,'testDB_2016-01-05.rot','2016-01-05','2016-01-05 00:00:00.000000','2016-01-06 00:00:00.000000',2.0,1,0,0,'/home/myles/Work/dbprocessing/functional_test/scripts/run_rot13_L1toL2.py /home/myles/Work/dbprocessing/functional_test/L1/testDB_2016-01-05.cat /tmp/tmpwtXMQO_testDB_2016-01-05.rot_runMe/testDB_2016-01-05.rot',NULL,NULL,NULL,'2018-05-11 19:29:42.399480',NULL,NULL,1,NULL,3,'a3e82427ddc673e684cc3bf9f6c2e5239cc2aa07',NULL);
CREATE TABLE process (
	process_id INTEGER NOT NULL, 
	process_name VARCHAR(50) NOT NULL, 
	output_product INTEGER, 
	output_timebase VARCHAR(10), 
	extra_params TEXT, 
	PRIMARY KEY (process_id), 
	UNIQUE (process_name, output_product), 
	FOREIGN KEY(output_product) REFERENCES product (product_id)
);
INSERT INTO process VALUES(1,'rot_L0toL1',1,'DAILY','a');
INSERT INTO process VALUES(2,'rot_L2toPlot',2,'RUN','a');
INSERT INTO process VALUES(3,'rot_L1toL2',3,'FILE','a');
CREATE TABLE instrumentproductlink (
	instrument_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	PRIMARY KEY (instrument_id, product_id), 
	FOREIGN KEY(instrument_id) REFERENCES instrument (instrument_id), 
	FOREIGN KEY(product_id) REFERENCES product (product_id)
);
INSERT INTO instrumentproductlink VALUES(1,1);
INSERT INTO instrumentproductlink VALUES(1,2);
INSERT INTO instrumentproductlink VALUES(1,3);
INSERT INTO instrumentproductlink VALUES(1,4);
CREATE TABLE inspector (
	inspector_id INTEGER NOT NULL, 
	filename VARCHAR(250) NOT NULL, 
	relative_path VARCHAR(250) NOT NULL, 
	description TEXT NOT NULL, 
	interface_version SMALLINT NOT NULL, 
	quality_version SMALLINT NOT NULL, 
	revision_version SMALLINT NOT NULL, 
	output_interface_version SMALLINT NOT NULL, 
	active_code BOOLEAN NOT NULL, 
	date_written DATE NOT NULL, 
	shasum VARCHAR(40), 
	newest_version BOOLEAN NOT NULL, 
	arguments TEXT, 
	product INTEGER NOT NULL, 
	PRIMARY KEY (inspector_id), 
	CHECK (interface_version >= 1), 
	CHECK (output_interface_version >= 1), 
	CHECK (active_code IN (0, 1)), 
	CHECK (newest_version IN (0, 1)), 
	FOREIGN KEY(product) REFERENCES product (product_id)
);
INSERT INTO inspector VALUES(1,'rot13_L1.py','codes/inspectors','Level 1',1,0,0,1,1,'2016-05-31',NULL,1,'-q',1);
INSERT INTO inspector VALUES(2,'rot13_L0.py','codes/inspectors','Level 0',1,0,0,1,1,'2016-05-31',NULL,1,'apid=001',2);
INSERT INTO inspector VALUES(3,'rot13_L2.py','codes/inspectors','Level 2',1,0,0,1,1,'2016-05-31',NULL,1,'-q',3);
INSERT INTO inspector VALUES(4,'rot13_L0.py','codes/inspectors','Level 0',1,0,0,1,1,'2016-05-31',NULL,1,'apid=000',4);
CREATE TABLE code (
	code_id INTEGER NOT NULL, 
	filename VARCHAR(250) NOT NULL, 
	relative_path VARCHAR(100) NOT NULL, 
	code_start_date DATE NOT NULL, 
	code_stop_date DATE NOT NULL, 
	code_description TEXT NOT NULL, 
	process_id INTEGER NOT NULL, 
	interface_version SMALLINT NOT NULL, 
	quality_version SMALLINT NOT NULL, 
	revision_version SMALLINT NOT NULL, 
	output_interface_version SMALLINT NOT NULL, 
	active_code BOOLEAN NOT NULL, 
	date_written DATE NOT NULL, 
	shasum VARCHAR(40), 
	newest_version BOOLEAN NOT NULL, 
	arguments TEXT, 
	ram FLOAT, 
	cpu SMALLINT, 
	PRIMARY KEY (code_id), 
	CHECK (code_start_date <= code_stop_date), 
	CHECK (interface_version >= 1), 
	CHECK (output_interface_version >= 1), 
	FOREIGN KEY(process_id) REFERENCES process (process_id), 
	CHECK (active_code IN (0, 1)), 
	CHECK (newest_version IN (0, 1))
);
INSERT INTO code VALUES(1,'run_rot13_L0toL1.py','scripts','2010-09-01','2020-01-01','Python L0->L1',1,1,0,0,1,1,'2016-05-31',NULL,1,NULL,1.0,1);
INSERT INTO code VALUES(2,'run_rot13_RUN_timebase.py','scripts','2010-09-01','2020-01-01','',2,1,0,0,1,1,'2016-05-31',NULL,1,NULL,1.0,1);
INSERT INTO code VALUES(3,'run_rot13_L1toL2.py','scripts','2010-09-01','2020-01-01','Python L1->L2',3,1,0,0,1,1,'2016-05-31',NULL,1,NULL,1.0,1);
CREATE TABLE filefilelink (
	source_file INTEGER NOT NULL, 
	resulting_file INTEGER NOT NULL, 
	PRIMARY KEY (source_file, resulting_file), 
	CHECK (source_file <> resulting_file), 
	FOREIGN KEY(source_file) REFERENCES file (file_id), 
	FOREIGN KEY(resulting_file) REFERENCES file (file_id)
);
INSERT INTO filefilelink VALUES(6,7);
INSERT INTO filefilelink VALUES(5,7);
INSERT INTO filefilelink VALUES(4,7);
INSERT INTO filefilelink VALUES(6,8);
INSERT INTO filefilelink VALUES(5,8);
INSERT INTO filefilelink VALUES(4,8);
INSERT INTO filefilelink VALUES(3,8);
INSERT INTO filefilelink VALUES(6,9);
INSERT INTO filefilelink VALUES(5,9);
INSERT INTO filefilelink VALUES(4,9);
INSERT INTO filefilelink VALUES(3,9);
INSERT INTO filefilelink VALUES(5,10);
INSERT INTO filefilelink VALUES(4,10);
INSERT INTO filefilelink VALUES(3,10);
INSERT INTO filefilelink VALUES(4,11);
INSERT INTO filefilelink VALUES(3,11);
INSERT INTO filefilelink VALUES(7,12);
INSERT INTO filefilelink VALUES(8,13);
INSERT INTO filefilelink VALUES(9,14);
INSERT INTO filefilelink VALUES(10,15);
INSERT INTO filefilelink VALUES(11,16);
CREATE TABLE productprocesslink (
	process_id INTEGER NOT NULL, 
	input_product_id INTEGER NOT NULL, 
	optional BOOLEAN NOT NULL, 
	yesterday INTEGER NOT NULL, 
	tomorrow INTEGER NOT NULL, 
	PRIMARY KEY (process_id, input_product_id), 
	FOREIGN KEY(process_id) REFERENCES process (process_id), 
	FOREIGN KEY(input_product_id) REFERENCES product (product_id), 
	CHECK (optional IN (0, 1))
);
INSERT INTO productprocesslink VALUES(1,4,0,2,2);
INSERT INTO productprocesslink VALUES(2,3,0,0,0);
INSERT INTO productprocesslink VALUES(3,1,0,0,0);
CREATE TABLE release (
	file_id INTEGER NOT NULL, 
	release_num VARCHAR(20) NOT NULL, 
	PRIMARY KEY (file_id, release_num), 
	FOREIGN KEY(file_id) REFERENCES file (file_id)
);
CREATE TABLE processqueue (
	file_id INTEGER NOT NULL, 
	version_bump SMALLINT, 
	PRIMARY KEY (file_id), 
	CHECK (version_bump is NULL or version_bump < 3), 
	FOREIGN KEY(file_id) REFERENCES file (file_id)
);
CREATE TABLE logging_file (
	logging_file_id INTEGER NOT NULL, 
	logging_id INTEGER NOT NULL, 
	file_id INTEGER NOT NULL, 
	code_id INTEGER NOT NULL, 
	comments TEXT, 
	PRIMARY KEY (logging_file_id), 
	FOREIGN KEY(logging_id) REFERENCES logging (logging_id), 
	FOREIGN KEY(file_id) REFERENCES file (file_id), 
	FOREIGN KEY(code_id) REFERENCES code (code_id)
);
CREATE TABLE filecodelink (
	resulting_file INTEGER NOT NULL, 
	source_code INTEGER NOT NULL, 
	PRIMARY KEY (resulting_file, source_code), 
	FOREIGN KEY(resulting_file) REFERENCES file (file_id), 
	FOREIGN KEY(source_code) REFERENCES code (code_id)
);
INSERT INTO filecodelink VALUES(7,1);
INSERT INTO filecodelink VALUES(8,1);
INSERT INTO filecodelink VALUES(9,1);
INSERT INTO filecodelink VALUES(10,1);
INSERT INTO filecodelink VALUES(11,1);
INSERT INTO filecodelink VALUES(12,3);
INSERT INTO filecodelink VALUES(13,3);
INSERT INTO filecodelink VALUES(14,3);
INSERT INTO filecodelink VALUES(15,3);
INSERT INTO filecodelink VALUES(16,3);
CREATE INDEX ix_product_product_id ON product (product_id);
CREATE INDEX ix_product_product_name ON product (product_name);
CREATE INDEX ix_file_data_level ON file (data_level);
CREATE INDEX ix_file_utc_start_time ON file (utc_start_time);
CREATE INDEX ix_file_utc_file_date ON file (utc_file_date);
CREATE UNIQUE INDEX ix_file_big ON file (filename, utc_file_date, utc_start_time, utc_stop_time);
CREATE INDEX ix_file_file_id ON file (file_id);
CREATE UNIQUE INDEX ix_file_filename ON file (filename);
CREATE INDEX ix_file_utc_stop_time ON file (utc_stop_time);
CREATE INDEX ix_process_output_product ON process (output_product);
CREATE INDEX ix_process_process_id ON process (process_id);
CREATE INDEX ix_process_output_timebase ON process (output_timebase);
CREATE INDEX ix_inspector_active_code ON inspector (active_code);
CREATE INDEX ix_inspector_inspector_id ON inspector (inspector_id);
CREATE INDEX ix_inspector_newest_version ON inspector (newest_version);
CREATE INDEX ix_code_code_id ON code (code_id);
CREATE INDEX ix_code_process_id ON code (process_id);
CREATE INDEX ix_filefilelink_source_file ON filefilelink (source_file);
CREATE INDEX ix_filefilelink_resulting_file ON filefilelink (resulting_file);
CREATE UNIQUE INDEX ix_processqueue_file_id ON processqueue (file_id);
COMMIT;
