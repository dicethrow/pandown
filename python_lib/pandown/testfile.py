from pandown import run_local_cmd, loggerClass
import colorama
import logging, sys

logging.setLoggerClass(loggerClass)
log = logging.getLogger(__name__)

if __name__ == "__main__":
	log.info("Starting...")
	
	log.info("Hello logging! from testfile.py")

	run_local_cmd("./xxxx.sh", 
		print_cmd = True)
		
	run_local_cmd("echo 'jdsfklj klj lkfjdslkjdsflkjlk jlkj lkfjlkdsj lkjsdflk jdslf kjsldkf jlks fjlksd jflksfd jlksd jflkds jflkf jslks jflks jlkfsdj lfdsji jsdlif jslidf jslid fjlis fjlsif jlsidjf lijflisdjf lisjdf lijsfdli jslij lifdsj ldsj slj fsli jfdsli jfs'", 
		print_cmd = True)

	log.info("Done")