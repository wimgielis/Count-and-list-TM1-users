import os
import sys

from TM1py.Services import TM1Service
from TM1py.Utils import get_all_servers_from_adminhost
from TM1py.Objects import User
from datetime import datetime


logline = []

def inspect_users():

    # =============================================================================================================
    # START of parameters and settings
    # =============================================================================================================

    # TM1 connection settings (IntegratedSecurityMode = 1 for now)
    ADDRESS = 'localhost'
    USER = 'wim'
    PWD = ''

    # level of detail in the output ==> 'YYYY':
    # - character 1: whether adding a header section with information for each TM1 model (Y/N)
    # - character 2: whether adding a section for an IBM user audit (Y/N)
    # - character 3: whether adding a section to list  the users in each TM1 model by their rights (Y/N)
    # - character 4: whether adding a section to list  the users in each TM1 model by their rights (Y/N)
    output_level = 'YYYY'

    ports_to_exclude = [8000]

    # use attributes (alias or text attribute or even numeric) to use 'better' user names for clients and/or groups
    # note: in case of a text or numeric attribute, there is a responsibility to provide unique names
    attribute_for_client_names = '}TM1_DefaultDisplayValue'

    ### START OF WORK IN PROGRESS (similar coding to client names)
    # attribute_for_group_names = '}TM1_DefaultDisplayValue'
    ### END OF WORK IN PROGRESS


    # =============================================================================================================
    # END of parameters and settings
    # =============================================================================================================


    # sanity checks
    output_level = output_level.replace(' ','').upper()
    if len(output_level) != 4:
        sys.exit('Level of output should contain 4 characters, with only Y or N. You now have: ' + output_level)

    if len(output_level.replace('Y','').replace('N','')) != 0:
        sys.exit('Level of output should contain 4 characters, with only Y or N. You now have: ' + output_level)

    header_or_customer = 'UPDATE THE CONSTANT WITH A DESCRIPTIVE HEADER OF YOUR LIKING'

    filehandle = open(r'D:\tm1_users.txt', 'w')

    global users_dictionary
    users_dictionary = {}


    if len(header_or_customer):
        logline.append('\n{}\n'.format(header_or_customer))

    if output_level[0] == 'Y':
        pa_versions = {
            '11.8.00100.13':['11.8.100.13', '11.8', '2.0.9.2', '27/07/2020'],
            '11.8.00000.33':['11.8.0.33', '11.8', '2.0.9.1', '21/05/2020'],
            '11.7.00000.42':['11.7.0.42', '11.7', '2.0.9', '16/12/2019'],
            '11.6.00000.14':['11.6.0.14', '11.6', '2.0.8', '17/07/2019'],
            '11.5.00000.23':['11.5.0.23', '11.5', '2.0.7', '29/04/2019'],
            '11.4.00003.8':['11.4.3.8', '11.4', '2.0.6 IF3', ''],
            '11.4.00000.21':['11.4.0.21', '11.4', '2.0.6', '11/10/2018'],
            '11.3.00003.1':['11.3.3.1', '11.3', '2.0.5 IF3', ''],
            '11.3.00000.27':['11.3.0.27', '11.3', '2.0.5', '25/06/2018'],
            '11.2.00000.27':['11.2.0.27', '11.2', '2.0.4', '16/02/2018'],
            '11.1.00004.2':['11.1.4.2', '11.1', '2.0.3 (dec 2017)','12/2017'],
            '11.1.00000.30':['11.1.0.30', '11.1', '2.0.3', '19/09/2017'],
            '11.0.00204.1030':['11.0.204.1030', '11.0', '2.0.2 IF4', ''],
            '11.0.00202.1014':['11.0.202.1014', '11.0', '2.0.2 IF2', ''],
            '11.0.00200.998':['11.0.200.998', '11.0', '2.0.2', '01/06/2017'],
            '11.0.00101.931':['11.0.101.931', '11.0', '2.0.1 IF1', ''],
            '11.0.00100.927-0':['11.0.100.927', '11.0', '2.0.1', '07/02/2017'],
            '11.0.00000.918':['11.0.00000.918', '11.0', '2.0.0', '16/12/2016']}

    # get TM1 models registered with the admin server
    tm1InstancesOnServer = get_all_servers_from_adminhost(ADDRESS)
    for tm1Instance in tm1InstancesOnServer:

        # get TM1 server information
        port = tm1Instance.http_port_number
        if port not in ports_to_exclude:
            SSL = tm1Instance.using_ssl

            tm1 = TM1Service(address=ADDRESS, port=port, user=USER, password=PWD, namespace='', gateway='', ssl=SSL)
            active_configuration = tm1.server.get_active_configuration()

            logline.append('\n=============  ' + tm1Instance.name + '  =============\n')

            if output_level[0] == 'Y':
                logline.append("Current time: " + datetime.now().strftime("%x %X"))

                try:
                    v = tm1.server.get_product_version()
                    logline.append('PA version information: ' + v + ' (' + (' | '.join(pa_versions[v])).strip(' | ') + ')')
                except KeyError:
                    logline.append('Unknown software version: ' + v)

                logline.append('Base TM1 REST API URL: ' + 'http' + ('s' if SSL else '') + '://' + ADDRESS + ':' + str(port) + '/api/v1/$metadata')
                logline.append('TM1 data directory: ' + os.path.abspath(tm1.server.get_data_directory()))
                logline.append('TM1 logging directory: ' + os.path.abspath(active_configuration["Administration"]["DebugLog"]["LoggingDirectory"]))
                logline.append('')
                logline.append('')

            if output_level[1] == 'Y' or output_level[2] == 'Y' or output_level[3] == 'Y':
                admin_users = []
                full_admin_users = []
                security_admin_users = []
                data_admin_users = []
                operations_admin_users = []
                non_admin_users = []
                authorized_users = []
                write_users = []
                read_users = []
                read_only_users = []
                disabled_users = []

                # custom security groups in TM1
                custom_groups = tm1.security.get_all_groups()
                try:
                    custom_groups.remove('ADMIN')
                    custom_groups.remove('DataAdmin')
                    custom_groups.remove('SecurityAdmin')
                    custom_groups.remove('OperationsAdmin')
                    custom_groups.remove('}tp_Everyone')
                except ValueError:
                    pass

                # get read-only users
                cubeContent = tm1.cells.execute_mdx_rows_and_values('SELECT {[}ClientProperties].[ReadOnlyUser]} ON COLUMNS, {[}Clients].MEMBERS} ON ROWS FROM [}ClientProperties]', False)
                for user in cubeContent:
                    if str(cubeContent[user][0]) != 'None':
                        read_only_users.append(str(user[0]))

                # get user types
                users = tm1.security.get_all_users()
                cubes = tm1.cubes.get_model_cubes()

                for user in users:
                    sUsername = str(user._name)
                    if user._enabled == False:
                        disabled_users.append(sUsername)
                    elif str(user._user_type) == 'Admin':
                        admin_users.append(sUsername)
                        full_admin_users.append(sUsername)
                    elif str(user._user_type) == 'SecurityAdmin':
                        admin_users.append(sUsername)
                        security_admin_users.append(sUsername)
                    elif str(user._user_type) == 'DataAdmin':
                        admin_users.append(sUsername)
                        data_admin_users.append(sUsername)
                    elif str(user._user_type) == 'OperationsAdmin':
                        admin_users.append(sUsername)
                        operations_admin_users.append(sUsername)
                    else:
                        non_admin_users.append(sUsername)
                        authorized_users.append(sUsername)
                        vClient_Access = ''
                        if sUsername not in read_only_users:
                            # loop over all application cubes
                            groups = tm1.security.get_groups(sUsername)
                            for cube in cubes:
                                for group in groups:
                                    sAccess = tm1.cells.get_value('}CubeSecurity', cube.name + ',' + str(group))
                                    if not sAccess in ['','None','Read']:
                                        vClient_Access = 'W'
                        if vClient_Access == 'W':
                            write_users.append(sUsername)
                        else:
                            read_users.append(sUsername)
                # output
                if output_level[1] == 'Y':

                    logline.append('User audit:')
                    logline.append('----------')
                    logline.append('')

                    output_count('Users', users, 0)
                    output_count('Full admin users (\'Administrator\')', full_admin_users, 1)
                    output_count('Read/write users (\'Authorized User\')', authorized_users, 1)
                    output_count('Read-only users (\'Explorer\')', read_only_users, 1)
                    output_count('Disabled users', disabled_users, 1)
                    if len(security_admin_users) > 0:
                        output_count('Security admin users', security_admin_users, 1)
                    if len(data_admin_users) > 0:
                        output_count('Data admin users', data_admin_users, 1)
                    if len(operations_admin_users) > 0:
                        output_count('Operations admin users', operations_admin_users, 1)
                    logline.append('')
                    logline.append('')

                if output_level[2] == 'Y':
                    logline.append('User count:')
                    logline.append('-----------')
                    logline.append('')

                    output_count('Users', users, 0)
                    output_count('Admin users', admin_users, 1)
                    output_count('Full admin users', full_admin_users, 2)
                    output_count('Security admin users', security_admin_users, 2)
                    output_count('Data admin users', data_admin_users, 2)
                    output_count('Operations admin users', operations_admin_users, 2)
                    logline.append('')
                    output_count('Non-admin users', non_admin_users, 1)
                    output_count('Read/write users', authorized_users, 2)
                    output_count('Write users', write_users, 3)
                    output_count('Read users', read_users, 3)
                    output_count('Read-only users', read_only_users, 2)
                    logline.append('')
                    output_count('Disabled users', disabled_users, 1)
                    logline.append('')
                    output_count('Custom TM1 security groups', custom_groups, 0)
                    logline.append('')
                    logline.append('')

            if output_level[3] == 'Y':

                # get attribute values for the users
                try:
                    mdx = f"""
                    SELECT
                    {{Tm1SubsetAll([}}Clients])}} ON ROWS,
                    {{[}}ElementAttributes_}}Clients].[{attribute_for_client_names}]}} ON COLUMNS
                    FROM [}}ElementAttributes_}}Clients]
                    """

                    rows_and_values = tm1.cells.execute_mdx_rows_and_values(mdx, False)
                    for row_elements, values in rows_and_values.items():
                        sUser = row_elements[0]
                        sAttr = str(values)
                        if sAttr.startswith('[\'') and sAttr.endswith('\']'):
                            # a string like ['Wim'] becomes Wim
                            sAttr = sAttr[2:-2]
                        else:
                            # a number like [205] becomes 205
                            sAttr = sAttr[1:-1]

                        if len(sAttr) > 0:
                            if sUser != sAttr:
                                users_dictionary[sUser] = sAttr
                except:
                    pass

                # output lists of usernames in the various lists
                logline.append('User lists:')
                logline.append('-----------')
                logline.append('')

                if len(security_admin_users) > 0 or len(data_admin_users) > 0 or len(operations_admin_users) > 0:
                    output_list('Admin users', admin_users)
                output_list('Full admin users', full_admin_users)
                output_list('Security admin users', security_admin_users)
                output_list('Data admin users', data_admin_users)
                output_list('Operations admin users', operations_admin_users)
                output_list('Non-admin users', non_admin_users)
                output_list('Read/write users', authorized_users)
                output_list('Write users', write_users)
                output_list('Read users', read_users)
                output_list('Read-only users', read_only_users)
                output_list('Disabled users', disabled_users)

                output_list('Custom TM1 security groups', custom_groups)

    filehandle.write("\n".join(logline))
    filehandle.close()
    return


def output_count(sText, lList, iIndent):

    sText = convert_text(sText, len(lList) == 1)
    logline.append("\t"*iIndent + str(len(lList)) + " " + sText )
    return

def output_list(sText, lList):

    if lList:

        lList = replace_username_in_list(lList, users_dictionary)
        lList.sort()

        sText = convert_text(sText, len(lList) == 1)

        logline.append(sText + " (" + str(len(lList)) + "):\n\t" + "\n\t".join(lList) + "\n" )
        return

def replace_username_in_list(lList, dDict):

    if len(lList) * len(dDict) == 0:
        return lList
    else:
        return [dDict.get(l, l) for l in lList]

def convert_text(sText, exactly_one):

    if exactly_one:
        sText = sText.replace('Users', 'User')
        sText = sText.replace('users', 'user')
        sText = sText.replace('groups', 'group')

    # convert the first character to lowercase
    return sText[0].lower() + sText[1:] if sText else ''

inspect_users()
