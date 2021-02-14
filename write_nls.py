#!/usr/bin/env python3

# Rewrite the NLS file with all the current sources listed.

import os
import in_place

VERSION_FILE = "profile/version.txt"

def write_nls(logger, source_list):
    if not os.path.exists("profile/nls"):
        try:
            os.makedirs("profile/nls")
        except:
            logger.error('Failed to make directory path for NLS file')
            return


    try:
        nls = open("profile/nls/en_us.txt", "w")

        nls.write("# controller\n")
        nls.write("ND-Volumio-NAME = Volumio\n")
        nls.write("ND-Volumio-ICON = Output\n")
        nls.write("ST-ctl-ST-NAME = NodeServer Online\n")
        nls.write("ST-ctl-GV0-NAME = Log Level\n")
        nls.write("ST-ctl-GV1-NAME = Selected Source\n")
        nls.write("ST-ctl-GV4-NAME = Shuffle\n")
        nls.write("ST-ctl-GV5-NAME = Repeat\n")
        nls.write("ST-ctl-MODE-NAME = State\n")
        nls.write("ST-ctl-SVOL-NAME = Volume\n")
        nls.write("CMD-ctl-PREV-NAME = Previous\n")
        nls.write("CMD-ctl-NEXT-NAME = Next\n")
        nls.write("CMD-ctl-PLAY-NAME = Play\n")
        nls.write("CMD-ctl-PAUSE-NAME = Pause\n")
        nls.write("CMD-ctl-STOP-NAME = Stop\n")
        nls.write("CMD-ctl-VOLUME-NAME = Volume\n")
        nls.write("CMD-ctl-SHUFFLE-NAME = Shuffle\n")
        nls.write("CMD-ctl-REPEAT-NAME = Repeat\n")
        nls.write("CMD-ctl-SOURCE-NAME = Selected Source\n")
        nls.write("CMD-ctl-DISCOVER-NAME = Re-Discover\n")
        nls.write("CMD-ctl-UPDATE_PROFILE-NAME = Update Profile\n")
        nls.write("CMD-ctl-DEBUG-NAME = Log Level\n")
        nls.write("\n")
        nls.write("DBG-0 = Off\n")
        nls.write("DBG-10 = Debug\n")
        nls.write("DBG-20 = Info\n")
        nls.write("DBG-30 = Warning\n")
        nls.write("DBG-40 = Error\n")
        nls.write("DBG-50 = Critical\n")
        nls.write("\n")
        nls.write("SWITCH-0 = Off\n")
        nls.write("SWITCH-1 = On\n")
        nls.write("\n")
        nls.write("MODE-0 = Stopped\n")
        nls.write("MODE-1 = Paused\n")
        nls.write("MODE-2 = Playing\n")
        nls.write("\n")

        cnt = 0
        for src in source_list:
            nls.write("SOURCE-{} = {}\n".format(cnt, src['name']))
            cnt += 1
        nls.close()
    except:
        logger.error('Failed to write NLS file')
        nls.close()

    with in_place.InPlace('profile/editor/editors.xml') as file:
        for line in file:
            if 'nls="SOURCE"' in line:
                file.write('\t\t<range uom="25" min="0" max="{}" nls="SOURCE" />\n'.format(cnt - 1))
            else:
                file.write(line)

