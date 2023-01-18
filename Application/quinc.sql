BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `vente` (
	`rowid`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`quantite`	INTEGER,
	`remise`	INTEGER,
	`idprod`	TEXT,
	`idcmd`	TEXT,
	FOREIGN KEY(`idprod`) REFERENCES `item`(`rowid`),
	FOREIGN KEY(`idcmd`) REFERENCES `commande`(`idcmd`)
);
INSERT INTO `vente` (rowid,quantite,remise,idprod,idcmd) VALUES (1,20,5,'3','201804050212'),
 (2,10,5,'1','201804050212'),
 (3,5,5,'2','201804050212'),
 (4,12,5,'4','201804050212'),
 (5,15,3,'5','201804050212'),
 (6,22,3,'10','201804061030'),
 (7,33,3,'11','201804061030'),
 (8,2,3,'12','201804061030'),
 (9,6,2,'13','201804061030');
CREATE TABLE IF NOT EXISTS `item` (
	`rowid`	INTEGER,
	`itemcode`	TEXT,
	`description`	TEXT,
	`unite`	TEXT,
	`quantite`	INTEGER DEFAULT 0,
	`pachat`	INTEGER,
	`pvente`	INTEGER,
	`fournisseur`	TEXT,
	`remarque`	TEXT,
	PRIMARY KEY(`rowid`)
);
INSERT INTO `item` (rowid,itemcode,description,unite,quantite,pachat,pvente,fournisseur,remarque) VALUES (1,'123544','dfghjbkkb','kg',541265,50,60,'dfghvjb','kjhgfghjb'),
 (2,'6541354','gfdfhjn','metre',542,2,3,'po','ghbjn'),
 (3,'684532','ddd','gr',546,5,9,'lkjhgfd','ttttt'),
 (4,'2222222','h','kg',50,5,6,'','jghk'),
 (5,'22333333','g','Litre',1000,1,2,'fdgx','poopo'),
 (6,'3333333','jlkllkj','Litre',50006,1,2,'ojlkkkj','hhjnk'),
 (8,'2125','g','lmkm',544351,24,5,'kljhk',''),
 (10,'543354','g','fdgdfgdf',465,534,542,'',''),
 (11,'554252','d','mm',0,50,60,'','dfgdf'),
 (12,'787777','y','mg',0,1,2,'','ioooop'),
 (13,'9898','uuuuuuu','PA',52,2,1,'erez','kpl'),
 (14,'999999','o','uuu',800,32,33,'mmmm','ghjk'),
 (15,'99900000','descripm noir 52	','tonne',2200,22,23,'Txr','fdgdf'),
 (16,'123544444','dfghjbkkb','kg',20,50,51,'',''),
 (17,'68453222222','ddd','gr',0,5,6,'','');
CREATE TABLE IF NOT EXISTS `commande` (
	`idcmd`	TEXT,
	`date`	TEXT,
	`validee`	INTEGER,
	PRIMARY KEY(`idcmd`)
);
INSERT INTO `commande` (idcmd,date,validee) VALUES ('201804050212','2018-04-05',NULL),
 ('201804061030','2018-04-06',NULL);
COMMIT;
