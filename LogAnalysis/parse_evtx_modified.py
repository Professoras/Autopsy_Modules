

import jarray
import inspect
import os
import subprocess

from javax.swing import JCheckBox
from javax.swing import JList
from javax.swing import JTextArea
from javax.swing import BoxLayout
from java.awt import GridLayout
from java.awt import BorderLayout
from javax.swing import BorderFactory
from javax.swing import JToolBar
from javax.swing import JPanel
from javax.swing import JFrame
from javax.swing import JScrollPane
from javax.swing import JComponent
from java.awt.event import KeyListener

from java.lang import Class
from java.lang import System
from java.sql import DriverManager, SQLException
from java.util.logging import Level
from java.io import File
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import GenericIngestModuleJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.coreutils import PlatformUtil
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.datamodel import ContentUtils


    # Where any setup and configuration is done
    # 'context' is an instance of org.sleuthkit.autopsy.ingest.IngestJobContext.
    # See: http://sleuthkit.org/autopsy/docs/api-docs/3.1/classorg_1_1sleuthkit_1_1autopsy_1_1ingest_1_1_ingest_job_context.html
    def startUp(self, context):
        self.context = context
        # Get path to EXE based on where this script is run from.
        # Assumes EXE is in same folder as script
        # Verify it is there before any ingest starts
        if PlatformUtil.isWindowsOS():
            self.path_to_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export_EVTX.exe")
            if not os.path.exists(self.path_to_exe):
                raise IngestModuleException("EXE was not found in module folder")
        pass

    # Where the analysis is done.
    # The 'dataSource' object being passed in is of type org.sleuthkit.datamodel.Content.
    # See: http://www.sleuthkit.org/sleuthkit/docs/jni-docs/interfaceorg_1_1sleuthkit_1_1datamodel_1_1_content.html
    # 'progressBar' is of type org.sleuthkit.autopsy.ingest.DataSourceIngestModuleProgress
    # See: http://sleuthkit.org/autopsy/docs/api-docs/3.1/classorg_1_1sleuthkit_1_1autopsy_1_1ingest_1_1_data_source_ingest_module_progress.html
    def process(self, dataSource, progressBar):

        # Check to see if the artifacts exist and if not then create it, also check to see if the attributes
        # exist and if not then create them
        skCase = Case.getCurrentCase().getSleuthkitCase();
        skCase_Tran = skCase.beginTransaction()
        try:
            self.log(Level.INFO, "Begin Create New Artifacts")
            artID_evtx = skCase.addArtifactType("CKC_TSK_EVTX_LOGS", "Windows Event Logs")
        except:
            self.log(Level.INFO, "Artifacts Creation Error, some artifacts may not exist now. ==> ")
            artID_evtx = skCase.getArtifactTypeID("CKC_TSK_EVTX_LOGS")

        try:
            self.log(Level.INFO, "Begin Create New Artifacts")
            artID_evtx_Long = skCase.addArtifactType("CKC_TSK_EVTX_LOGS_LONG", "Windows Event Logs Long Tail Analysis")
        except:
            self.log(Level.INFO, "Artifacts Creation Error, some artifacts may not exist now. ==> ")
            artID_evtx_Long = skCase.getArtifactTypeID("CKC_TSK_EVTX_LOGS")

        try:
            attID_ev_fn = skCase.addArtifactAttributeType("TSK_EVTX_FILE_NAME",
                                                          BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING,
                                                          "Event Log File Name")
        except:
            self.log(Level.INFO, "Attributes Creation Error, Event Log File Name. ==> ")
        try:
            attID_ev_rc = skCase.addArtifactAttributeType("TSK_EVTX_RECOVERED_RECORD",
                                                          BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING,
                                                          "Recovered Record")
        except:
            self.log(Level.INFO, "Attributes Creation Error, Recovered Record. ==> ")
        try:
            attID_ev_cn = skCase.addArtifactAttributeType("TSK_EVTX_COMPUTER_NAME",
                                                          BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING,
                                                          "Computer Name")
        except:
            self.log(Level.INFO, "Attributes Creation Error, Computer Name. ==> ")
        try:
            attID_ev_ei = skCase.addArtifactAttributeType("TSK_EVTX_EVENT_IDENTIFIER",
                                                          BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG,
                                                          "Event Identiifier")
        except:
            self.log(Level.INFO, "Attributes Creation Error, Event Log File Name. ==> ")
        try:
            attID_ev_eiq = skCase.addArtifactAttributeType("TSK_EVTX_EVENT_IDENTIFIER_QUALIFERS",
                                                           BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING,
                                                           "Event Identifier Qualifiers")
        except:
            self.log(Level.INFO, "Attributes Creation Error, Event Identifier Qualifiers. ==> ")
        try:
            attID_ev_el = skCase.addArtifactAttributeType("TSK_EVTX_EVENT_LEVEL",
                                                          BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING,
                                                          "Event Level")
        except:
            self.log(Level.INFO, "Attributes Creation Error, Event Level. ==> ")
        try:
            attID_ev_oif = skCase.addArtifactAttributeType("TSK_EVTX_OFFSET_IN_FILE",
                                                           BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING,
                                                           "Event Offset In File")
        except:
            self.log(Level.INFO, "Attributes Creation Error, Event Offset In File. ==> ")
        try:
            attID_ev_id = skCase.addArtifactAttributeType("TSK_EVTX_IDENTIFIER",
                                                          BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING,
                                                          "Identifier")
        except:
            self.log(Level.INFO, "Attributes Creation Error, Identifier. ==> ")
        try:
            attID_ev_sn = skCase.addArtifactAttributeType("TSK_EVTX_SOURCE_NAME",
                                                          BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING,
                                                          "Source Name")
        except:
            self.log(Level.INFO, "Attributes Creation Error, Source Name. ==> ")
        try:
            attID_ev_usi = skCase.addArtifactAttributeType("TSK_EVTX_USER_SECURITY_ID",
                                                           BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING,
                                                           "User Security ID")
        except:
            self.log(Level.INFO, "Attributes Creation Error, User Security ID. ==> ")
        try:
            attID_ev_et = skCase.addArtifactAttributeType("TSK_EVTX_EVENT_TIME",
                                                          BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING,
                                                          "Event Time")
        except:
            self.log(Level.INFO, "Attributes Creation Error, Event Time. ==> ")
        try:
            attID_ev_ete = skCase.addArtifactAttributeType("TSK_EVTX_EVENT_TIME_EPOCH",
                                                           BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING,
                                                           "Event Time Epoch")
        except:
            self.log(Level.INFO, "Attributes Creation Error, Identifier. ==> ")
        try:
            attID_ev_dt = skCase.addArtifactAttributeType("TSK_EVTX_EVENT_DETAIL_TEXT",
                                                          BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING,
                                                          "Event Detail")
        except:
            self.log(Level.INFO, "Attributes Creation Error, Event Detail. ==> ")

        try:
            attID_ev_cnt = skCase.addArtifactAttributeType("TSK_EVTX_EVENT_ID_COUNT",
                                                           BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.LONG,
                                                           "Event Id Count")
        except:
            self.log(Level.INFO, "Attributes Creation Error, Event ID Count. ==> ")

        # self.log(Level.INFO, "Get Artifacts after they were created.")
        # Get the new artifacts and attributes that were just created
        artID_evtx = skCase.getArtifactTypeID("CKC_TSK_EVTX_LOGS")
        artID_evtx_evt = skCase.getArtifactType("CKC_TSK_EVTX_LOGS")
        artID_evtx_Long = skCase.getArtifactTypeID("CKC_TSK_EVTX_LOGS_LONG")
        artID_evtx_Long_evt = skCase.getArtifactType("CKC_TSK_EVTX_LOGS_LONG")
        attID_ev_fn = skCase.getAttributeType("TSK_EVTX_FILE_NAME")
        attID_ev_rc = skCase.getAttributeType("TSK_EVTX_RECOVERED_RECORD")
        attID_ev_cn = skCase.getAttributeType("TSK_EVTX_COMPUTER_NAME")
        attID_ev_ei = skCase.getAttributeType("TSK_EVTX_EVENT_IDENTIFIER")
        attID_ev_eiq = skCase.getAttributeType("TSK_EVTX_EVENT_IDENTIFIER_QUALIFERS")
        attID_ev_el = skCase.getAttributeType("TSK_EVTX_EVENT_LEVEL")
        attID_ev_oif = skCase.getAttributeType("TSK_EVTX_OFFSET_IN_FILE")
        attID_ev_id = skCase.getAttributeType("TSK_EVTX_IDENTIFIER")
        attID_ev_sn = skCase.getAttributeType("TSK_EVTX_SOURCE_NAME")
        attID_ev_usi = skCase.getAttributeType("TSK_EVTX_USER_SECURITY_ID")
        attID_ev_et = skCase.getAttributeType("TSK_EVTX_EVENT_TIME")
        attID_ev_ete = skCase.getAttributeType("TSK_EVTX_EVENT_TIME_EPOCH")
        attID_ev_dt = skCase.getAttributeType("TSK_EVTX_EVENT_DETAIL_TEXT")
        attID_ev_cnt = skCase.getAttributeType("TSK_EVTX_EVENT_ID_COUNT")

        # we don't know how much work there is yet
        progressBar.switchToIndeterminate()

        # Find the Windows Event Log Files
        files = []
        fileManager = Case.getCurrentCase().getServices().getFileManager()
        files = fileManager.findFiles(dataSource, "%.evtx")


        numFiles = len(files)
        self.log(Level.INFO, "found " + str(numFiles) + " files")
        progressBar.switchToDeterminate(numFiles)
        fileCount = 0;

        # Create Event Log directory in temp directory, if it exists then continue on processing
        Temp_Dir = Case.getCurrentCase().getTempDirectory()
        self.log(Level.INFO, "create Directory " + Temp_Dir)
        temp_dir = os.path.join(Temp_Dir, "EventLogs")
        try:
            os.mkdir(temp_dir)
        except:
            self.log(Level.INFO, "Event Log Directory already exists " + temp_dir)

        # Write out each Event Log file to the temp directory
        for file in files:

            # Check if the user pressed cancel while we were busy
            if self.context.isJobCancelled():
                return IngestModule.ProcessResult.OK

            # self.log(Level.INFO, "Processing file: " + file.getName())
            fileCount += 1

            # Save the DB locally in the temp folder. use file id as name to reduce collisions
            lclDbPath = os.path.join(temp_dir, file.getName())
            ContentUtils.writeToFile(file, File(lclDbPath))

        # Run the EXE, saving output to a sqlite database
        self.log(Level.INFO,
                 "Running program on data source " + self.path_to_exe + " parm 1 ==> " + temp_dir + "  Parm 2 ==> " + os.path.join(
                     temp_dir, "EventLogs.db3"))
        subprocess.Popen([self.path_to_exe, temp_dir, os.path.join(Temp_Dir, "EventLogs.db3")]).communicate()[0]

        # Set the database to be read to the one created by the Event_EVTX program
        lclDbPath = os.path.join(Case.getCurrentCase().getTempDirectory(), "EventLogs.db3")
        self.log(Level.INFO, "Path to the Eventlogs database file created ==> " + lclDbPath)

        # Open the DB using JDBC
        try:
            Class.forName("org.sqlite.JDBC").newInstance()
            dbConn = DriverManager.getConnection("jdbc:sqlite:%s" % lclDbPath)
        except SQLException as e:
            self.log(Level.INFO,
                     "Could not open database file (not SQLite) " + file.getName() + " (" + e.getMessage() + ")")
            return IngestModule.ProcessResult.OK

        files = []
        fileManager = Case.getCurrentCase().getServices().getFileManager()
        files = fileManager.findFiles(dataSource, "%.evtx")

        for file in files:
            file_name = file.getName()
            self.log(Level.INFO, "File To process in SQL " + file_name + "  <<=====")
            # Query the contacts table in the database and get all columns.
            try:
                stmt = dbConn.createStatement()
                SQL_Statement = "SELECT File_Name, Recovered_Record, Computer_name, Event_Identifier, " + \
                                " Event_Identifier_Qualifiers, Event_Level, Event_offset, Identifier, " + \
                                " Event_source_Name, Event_User_Security_Identifier, Event_Time, " + \
                                " Event_Time_Epoch, Event_Detail_Text FROM Event_Logs where upper(File_Name) = upper('" + file_name + "')"
                # self.log(Level.INFO, "SQL Statement " + SQL_Statement + "  <<=====")
                resultSet = stmt.executeQuery(SQL_Statement)
            except SQLException as e:
                self.log(Level.INFO, "Error querying database for EventLogs table (" + e.getMessage() + ")")
                return IngestModule.ProcessResult.OK

            # Cycle through each row and create artifacts
            while resultSet.next():
                try:
                    # File_Name  = resultSet.getString("File_Name")
                    # Recovered_Record = resultSet.getString("Recovered_Record")
                    Computer_Name = resultSet.getString("Computer_Name")
                    Event_Identifier = resultSet.getInt("Event_Identifier")
                    # Event_Identifier_Qualifiers = resultSet.getString("Event_Identifier_Qualifiers")
                    Event_Level = resultSet.getString("Event_Level")
                    # Event_Offset = resultSet.getString("Event_Offset")
                    # Identifier = resultSet.getString("Identifier")
                    Event_Source_Name = resultSet.getString("Event_Source_Name")
                    Event_User_Security_Identifier = resultSet.getString("Event_User_Security_Identifier")
                    Event_Time = resultSet.getString("Event_Time")
                    # Event_Time_Epoch = resultSet.getString("Event_Time_Epoch")
                    Event_Detail_Text = resultSet.getString("Event_Detail_Text")
                except SQLException as e:
                    self.log(Level.INFO, "Error getting values from contacts table (" + e.getMessage() + ")")

                # Make an artifact on the blackboard, TSK_PROG_RUN and give it attributes for each of the fields
                # Make artifact for CKC_TSK_EVTX_LOGS
                art = file.newArtifact(artID_evtx)

                art.addAttributes(
                    ((BlackboardAttribute(attID_ev_cn, ParseEvtxDbIngestModuleFactory.moduleName, Computer_Name)), \
                     (BlackboardAttribute(attID_ev_ei, ParseEvtxDbIngestModuleFactory.moduleName,
                                          Event_Identifier)), \
                     (BlackboardAttribute(attID_ev_el, ParseEvtxDbIngestModuleFactory.moduleName, Event_Level)), \
                     (BlackboardAttribute(attID_ev_sn, ParseEvtxDbIngestModuleFactory.moduleName,
                                          Event_Source_Name)), \
                     (BlackboardAttribute(attID_ev_usi, ParseEvtxDbIngestModuleFactory.moduleName,
                                          Event_User_Security_Identifier)), \
                     (BlackboardAttribute(attID_ev_et, ParseEvtxDbIngestModuleFactory.moduleName, Event_Time)), \
                     (BlackboardAttribute(attID_ev_dt, ParseEvtxDbIngestModuleFactory.moduleName,
                                          Event_Detail_Text))))
                # These attributes may also be added in the future
                # art.addAttribute(BlackboardAttribute(attID_ev_fn, ParseEvtxDbIngestModuleFactory.moduleName, File_Name))
                # art.addAttribute(BlackboardAttribute(attID_ev_rc, ParseEvtxDbIngestModuleFactory.moduleName, Recovered_Record))
                # art.addAttribute(BlackboardAttribute(attID_ev_eiq, ParseEvtxDbIngestModuleFactory.moduleName, Event_Identifier_Qualifiers))
                # art.addAttribute(BlackboardAttribute(attID_ev_oif, ParseEvtxDbIngestModuleFactory.moduleName, Event_Offset))
                # art.addAttribute(BlackboardAttribute(attID_ev_id, ParseEvtxDbIngestModuleFactory.moduleName, Identifier))
                # art.addAttribute(BlackboardAttribute(attID_ev_ete, ParseEvtxDbIngestModuleFactory.moduleName, Event_Time_Epoch))

            try:
                stmt_1 = dbConn.createStatement()
                SQL_Statement_1 = "select event_identifier, file_name, count(*) 'Number_Of_Events'  " + \
                                  " FROM Event_Logs where upper(File_Name) = upper('" + file_name + "')" + \
                                  " group by event_identifier, file_name order by 3;"
                # self.log(Level.INFO, "SQL Statement " + SQL_Statement_1 + "  <<=====")
                resultSet_1 = stmt_1.executeQuery(SQL_Statement_1)
            except SQLException as e:
                self.log(Level.INFO, "Error querying database for EventLogs table (" + e.getMessage() + ")")
                return IngestModule.ProcessResult.OK

            # Cycle through each row and create artifacts
            while resultSet_1.next():
                try:
                    # File_Name  = resultSet.getString("File_Name")
                    # Recovered_Record = resultSet.getString("Recovered_Record")
                    Event_Identifier = resultSet_1.getInt("Event_Identifier")
                    Event_ID_Count = resultSet_1.getInt("Number_Of_Events")
                except SQLException as e:
                    self.log(Level.INFO, "Error getting values from contacts table (" + e.getMessage() + ")")

                # Make an artifact on the blackboard, TSK_PROG_RUN and give it attributes for each of the fields
                # Make artifact for CKC_TSK_EVTX_LOGS
                art_1 = file.newArtifact(artID_evtx_Long)

                self.log(Level.INFO, "Type of Object is ==> " + str(type(Event_ID_Count)))

                art_1.addAttributes(((BlackboardAttribute(attID_ev_ei, ParseEvtxDbIngestModuleFactory.moduleName,
                                                          Event_Identifier)), \
                                     (BlackboardAttribute(attID_ev_cnt, ParseEvtxDbIngestModuleFactory.moduleName,
                                                          Event_ID_Count))))

            # Fire an event to notify the UI and others that there are new artifacts
            IngestServices.getInstance().fireModuleDataEvent(
                ModuleDataEvent(ParseEvtxDbIngestModuleFactory.moduleName, artID_evtx_evt, None))
            IngestServices.getInstance().fireModuleDataEvent(
                ModuleDataEvent(ParseEvtxDbIngestModuleFactory.moduleName, artID_evtx_Long_evt, None))

            # Clean up
            stmt_1.close()
            stmt.close()
            dbConn.close()
            os.remove(lclDbPath)

            # Clean up EventLog directory and files
            for file in files:
                try:
                    os.remove(os.path.join(temp_dir, file.getName()))
                except:
                    self.log(Level.INFO, "removal of Event Log file failed " + os.path.join(temp_dir, file.getName()))
            try:
                os.rmdir(temp_dir)
            except:
                self.log(Level.INFO, "removal of Event Logs directory failed " + temp_dir)

            # Fire an event to notify the UI and others that there are new artifacts
            IngestServices.getInstance().fireModuleDataEvent(
                ModuleDataEvent(ParseEvtxDbIngestModuleFactory.moduleName, artID_evtx_evt, None))

            # After all databases, post a message to the ingest messages in box.
            message = IngestMessage.createMessage(IngestMessage.MessageType.DATA,
                                                  "ParseEvtx", " Event Logs have been parsed ")
            IngestServices.getInstance().postMessage(message)

            # Fire an event to notify the UI and others that there are new artifacts
            IngestServices.getInstance().fireModuleDataEvent(
                ModuleDataEvent(ParseEvtxDbIngestModuleFactory.moduleName, artID_evtx_evt, None))

            return IngestModule.ProcessResult.OK
