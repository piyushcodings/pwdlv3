import argparse
from error import errorList
from utils.glv import Global
import sys
from utils.os2 import SysFunc
import os
from main import Main
from startup.checkup import CheckState

# global variables
prefs = {}
glv = Global()
os2 = SysFunc()

# hardcoding the list of executables required for the script to run
# should be available in the PATH or the user should provide the path to the executables
EXECUTABLES = ['ffmpeg', 'mp4decrypt', 'nm3']


def main():

    # parsing the arguments
    parser = argparse.ArgumentParser(description='PhysicsWallah M3u8 parser.')

    parser.add_argument('--csv-file', type=str, help='Input csv file. Legacy Support too.')
    parser.add_argument('--id', type=str,
                        help='PhysicsWallh Video Id for single usage. Incompatible with --csv-file.   Must be used with --name')
    parser.add_argument('--name', type=str,
                        help='Name for the output file. Incompatible with --csv-file.   Must be used with --url')
    parser.add_argument('--dir', type=str, help='Output Directory')
    parser.add_argument('--verbose', action='store_true', help='Verbose Output')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--simulate', action='store_true',
                        help='Simulate the download process. No files will be downloaded.)')

    args = parser.parse_args()

    # user_input is given preference i.e if --verbose is true it will override
    # however if --verbose is false but prefs['verbose'] is true 
    glv.vout = args.verbose

    global prefs

    # check if all dependencies are installed
    state = CheckState().checkup(EXECUTABLES, verbose=glv.vout)
    prefs = state['prefs']

    # --------------------------------------------------------------------------------------------------------------------------------------

    # loading user preferences from the defaults.json file

    # setting verbose output
    if not glv.vout and prefs['verbose']: glv.vout = prefs['verbose']

    # checking for tmpDir
    if 'tmpDir' in prefs:
        tmpDir = SysFunc.modify_path(prefs['tmpDir'])
        if not os.path.exists(tmpDir):
            os.makedirs(tmpDir)
    else:
        prefs['tmpDir'] = './tmp/'

    # setting up tmp directory
    if glv.vout: Global.hr(); glv.dprint(f"Tmp Dir is: {SysFunc.modify_path(prefs['tmpDir'])}")

    # setting up output directory
    if args.dir:
        OUT_DIRECTORY = os.path.abspath(os.path.expandvars(args.dir))
    else:
        OUT_DIRECTORY = './'
    if glv.vout: Global.hr(); glv.dprint(f'Output Directory: {OUT_DIRECTORY}')

    # setting up hr
    if not 'hr' in prefs:
        Global.disable_hr = False
    elif not prefs['hr']:
        Global.disable_hr = True

    if glv.vout: Global.hr(); glv.dprint(f"Horizontal Rule: {not Global.disable_hr}")

    # --------------------------------------------------------------------------------------------------------------------------------------
    # end of loading user preferences


    # starting the main process

    #if both csv file and (url or name) is provided then -> exit with error code 3
    if args.csv_file and (args.id or args.name):
        print("Both csv file and id (or name) is provided. Unable to decide. Aborting! ...")
        sys.exit(3)

    # handle in case --csv-file is provided
    if args.csv_file:

        # simulation mode
        if args.simulate:
            print("Simulating the download csv process. No files will be downloaded.")
            print("File to be processed: ", args.csv_file)
            exit(0)

        # exiting in case the CSV File is not found
        if not os.path.exists(args.csv_file):
            errorList['csvFileNotFound']['func'](args.csv_file)
            sys.exit(errorList['csvFileNotFound']['code'])

        with open(args.csv_file, 'r') as f:
            for line in f:
                name, id = line.strip().split(',')

                # adding support for csv file with partial errors
                try:
                    Main(id=id,
                         name=name,
                         directory=OUT_DIRECTORY,
                         ffmpeg=state['ffmpeg'],
                         nm3Path=state['nm3'],
                         mp4d=state['mp4decrypt'],
                         tmpDir=prefs['tmpDir'],
                         verbose=glv.vout,
                         suppress_exit=True  # suppress exit in case of error (as multiple files are being processed)
                         ).process()

                except Exception as e:
                    errorList['downloadFailed']['func'](name, id)



    # handle in case key and name is given 
    elif args.id and args.name:

        # simulation mode
        if args.simulate:
            print("Simulating the download process. No files will be downloaded.")
            print("Id to be processed: ", args.id)
            print("Name to be processed: ", args.name)
            exit(0)

        try:

            Main(id=args.id,
                 name=args.name,
                 directory=OUT_DIRECTORY,
                 ffmpeg=state['ffmpeg'],
                 nm3Path=state['nm3'],
                 mp4d=state['mp4decrypt'],
                 tmpDir=prefs['tmpDir'],
                 verbose=glv.vout).process()

        except Exception as e:

            errorList['downloadFailed']['func'](args.name, args.id)
            sys.exit(errorList['downloadFailed']['code'])

    # in case neither is used 
    else:
        exit(1)


if __name__ == "__main__":
    main()
