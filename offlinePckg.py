import sys
import os
import subprocess
import time
import argparse

parser = argparse.ArgumentParser(description="Grab All Dependencies")
parser.add_argument('--distro', default="xenial",
    help='Target distribution for the packages requested.')
parser.add_argument('libs', nargs="+",
    help='Libraries to pull.')
parser.add_argument('arch', default='amd64',
    help="Architecture being imported.")

args = parser.parse_args()
distro = args.distro #=xenial
debList = args.libs
#march_=architecture #=amd64
#debList.pop(0)
#numDeb = len(sys.argv)
#debList = sys.argv
urlh = ''
if distro == 'lucid':
	urlh = 'https://launchpad.net/ubuntu/' #' lucid/amd64/libnotify-dev/'
else:
	urlh = "https://packages.ubuntu.com/"
urld = "/download"
missed_list = []
cwd = os.getcwd()
cwf = cwd + "/file"
pkF = open("pckg.list", "r")
pckg_list = pkF.readlines()
pkF.close()
pkF = open("pckg.list", "a")
dpF = open("dpkg.list", "r")
fin_deb_list = dpF.readlines()
dpF.close()
dpF = open("dpkg.list", "a")
newlist = []
newdeb_deb = []

def findDelimSubstr(targStr, firstDelim, secondDDelim, index=0):
    strBeg = targStr.find(firstDelim, index)
    strEnd = targStr.find(secondDDelim, strBeg + len(firstDelim))
    resStr = targStr[strBeg:strEnd]

    name_beg = fdata.rfind("\x2f", link_beg, link_end)
    newlink = fdata[link_beg + 1:link_end - len(fdata)]
    return resStr


def resolveError(fdata):
	if distro == 'lucid':
		if "Page not found" in fdata:
			return True
	else:
		# if fdata.find("Error</title>") != -1:
		if "Error</title>" in fdata:
			return True
	return False

def getPkgPageUrl(pkg, march, append):
	url = urlh + distro + '/'
	if distro == 'lucid':
		url = url + march + '/'
	url = url + pkg
	if append:
		if distro != 'lucid':
			url = url + urld

	if distro == 'lucid':
		subprocess.call("wget -O file " + url, shell=True)
		g = open("file", 'r')
		gdata = g.read()
		if resolveError(gdata):
			g.close()
			return False
		# "/ubuntu/lucid/amd64"
		ind = gdata.find("\"/ubuntu/" + distro + "/" + march + "\"")
		ind = gdata.find("<a href=\"", ind) + len("<a href=\"")
		ind_ = gdata.find('\"', ind)
		package = gdata[ind:ind_]
		packageSuffix = package.rfind('/')
		packageSuffix = package[packageSuffix:]
		url = url + packageSuffix
	return url



def grab_pckg(pckg_, march="amd64"):
	if os.path.isfile(cwf):
		os.remove(cwf)
	#	subprocess.check_call("rm " + cwf, shell=True)
	# url = urlh + distro + "/" + march + "/" + pckg_ + urld #xenial/amd64/
	url = getPkgPageUrl(pckg_, march, True)
	print("GETTING URL: {}\n\n\n\n\n".format(url))
	subprocess.call("wget -O file " + url, shell=True)
	f = open("file", 'r')
	fdata = f.read()
	if resolveError(fdata):
		f.close()
		march = "all"
		url = urlh + distro + "/" + march + "/" + pckg_ + urld #xenial/amd64/
		print("FAILED ARCH, FETCHING URL: {}\n\n\n\n\n".format(url))
		subprocess.call("wget -O file " + url, shell=True)
		f = open("file", "r")
	if distro == 'lucid':
		ind = fdata.find('Downloadable files')
	else:
		ind = fdata.find("<li>")
	ind_ = fdata.find('href=\"http', ind)

	if ind_ != -1:
		link_beg = fdata.find('\"', ind_)
		link_end = fdata.find('\"', link_beg + 1)
		name_beg = fdata.rfind("\x2f", link_beg, link_end)
		name_out = fdata[name_beg + 1:link_end - len(fdata)]
		newlink = fdata[link_beg + 1:link_end - len(fdata)]
#       newdeb = wget.download(fdata[link_beg:link_end - len(fdata)])
		print("GETTING DEB: {}\n\n\n\n\n".format(url))
		subprocess.call("wget -O " + name_out + " " + newlink, shell=True)
		newdeb_deb.append(name_out)

	else:
		missed_list.append(pckg_)
	f.close()
	subprocess.check_call("rm file", shell=True)

def grab_dep(pckg_, march="amd64"):
	# url = urlh + distro + "/" + pckg_
	url = getPkgPageUrl(pckg_, march, False)
	print("GETTING RELIABLES: {}\n\n\n\n\n".format(url))
	subprocess.call("wget -O file " + url, shell=True)
	g = open("file", 'r')
	gdata = g.read()
	if resolveError(gdata):
		missed_list.append(pckg_)
		g.close()
		return

	grab_str = "dep:</span>" #"dep:</span><span>&lt;/<span class=\"end-tag\">"
	ind = 0
	endCond = 0
	if distro == 'lucid':
		ind = gdata.find("<dl id=\"depends\">")
	else:
		ind = gdata.find(grab_str)
	endCond = gdata.find('</div>', ind)
	#get start condition
	lib_ = ''
	while (True):
		
		#check error condition
		# ind_ = gdata.find(grap_str, ind + 1)
		# if ind_ == -1:
		# 	break

		addr_lib = gdata.find(distro + "/", ind + 1)
		if (addr_lib > endCond) or (addr_lib == -1):
			break
		addr_lib = addr_lib + len(distro + "/")
		addr_end = gdata.find("\"", addr_lib)

		lib = gdata[addr_lib:addr_end - len(gdata)]
		newLib = lib.split('/')
		lib = newLib[1]
		targetArch = newLib[0]

		lib_ = lib + ":" + targetArch
		if (lib_ + "\n") not in pckg_list:
			if lib_ not in newlist:
				newlist.append(lib_)
				grab_dep(lib, targetArch)
		# if march == "i386":
		# 	lib_64 = lib + ":amd64"
		# 	if (lib_64 + "\n") not in pckg_list:
		# 		if lib_64 not in newlist:
		# 			newlist.append(lib_64)
		# 			grab_dep(lib)
		ind = addr_end
	lib_ = pckg_ + ':' + march
	if (lib_ + "\n") not in pckg_list:
		if lib_ not in newlist:
			newlist.append(lib_)
	# if march == "i386":
	# 	lib_64 = lib + ":amd64"
	# 	if (lib_64 + "\n") not in pckg_list:
	# 		if lib_64 not in newlist:
	# 			newlist.append(pckg_ + ":" + march)
	g.close()

def main():
#	numDeb = len(sys.argv)
#	debList = sys.argv
#	debList.pop(0)
	for i in debList:
		if ":i386" in i:
			grab_dep(i[:i.find(":i386") - len(i)], "i386")
		elif ":amd64" in i:
			grab_dep(i[:i.find(":amd64") - len(i)])
		else:
			grab_dep(i)
	for i in newlist:
		if ":i386" in i:
			grab_pckg(i[:i.find(":i386") - len(i)], "i386")
		elif ":amd64" in i:
			grab_pckg(i[:i.find(":amd64") - len(i)])
		else:
			grab_pckg(i)
	if len(missed_list) > 0:
		print("failed to retrieve")
		for i in missed_list:
			print("\t\t{}".format(i))
	for i in newlist:
		pkF.write(i + "\n")
	for i in newdeb_deb:
		dpF.write(i + "\n")
	pkF.close()
	dpF.close()
	if len(newlist) > 0:
		subprocess.call("./finish.sh", shell=True)

if __name__ == "__main__":
	main()