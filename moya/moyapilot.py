from __future__ import unicode_literals

from collections import namedtuple
from threading import local
from .console import Console
from .compat import implements_to_string
from .interface import ObjectExposer
from .import settings
from .moyaexceptions import MoyaException

import os
import io


class _LocalAttribute(object):
    """An attribute that belongs to thread locals"""

    def __init__(self, name, callable=None):
        self.name = name
        self.callable = callable or (lambda: None)

    def __get__(self, obj, type=None):
        if not hasattr(obj._local, self.name):
            setattr(obj._local, self.name, self.callable())
        return getattr(obj._local, self.name)

    def __set__(self, obj, value):
        setattr(obj._local, self.name, value)

    def __delete__(self, obj):
        if hasattr(obj._local, self.name):
            delattr(obj._local, self.name)


_ascii_pilot = """\
@@@@@@@###''''+'##########+++'#+#########;++###################@@@@@@#######@#@@@@@@@@@@@@@@@+###@@@+
@@@@@@@##'''+'+###########++++#+#########;+###############@@###@#@@@@@######@@@@@@@@@@@@@@@@@#+####@@
@@@@@###+''++############++++#+##########:+#####+++++##########@@@@@@@######@@@@@@@#@@@@@@@@@#+#####@
@@@@##++++#+############++++#+###########:+''''''''''''''++#####@@@@@@@##@#@@@@@@##@#@@@@@@@@@++#####
@@@###+++#+#############+#++++##########+;'++'+''''''''''''+#####@@@@@@#@@@@@@@@######@@@@@@@@#+##@@#
@@@#############++#+###+#++#+#########++#+++++''++';;;;;';'+'++++++####################@@@@@@@@##@@@@
@@##############+++++#+####+#####+++'+++'''';;;;;;:,...,,:'''''++''++++++++#####@##@####@@@@@@@@@@@@@
################+++++++###++++''+'+'+''''';;;::,,,.`````.,:;';'''''''''+''+'+++++#####@#@@@@@@@@@@@@@
###############+++++++#+++++++++++++++++''';;::,..`` ```.,::::;;'+';;;''+'';'''''+#####@#@@@@@@@@@@@@
###############+++'+++++++++'''+++'++++++#++++'+''''';;;'::;;''''+++'+#++++++++''''';'####@@@@@@@@@@@
#@############+++++++''''+++++++############+++###++';'''''+''++'++##@@@@@@######++'++''+##@@@@@@@@@@
@#############+';'++#####@@@@@@@@##@######@@@@@@@@##+++++++#@@@#;:;::,:'#@@@@@#######++#+;'#@@@@@@@@@
############+'+####@@@@@@@@##+''''+######@#+#@@@@@@@@#+';+@@@@##',:;:''';;;'#@@@####+##+++;;##@@@@@@@
##########'+++####@@@@###+'+####@@@@@@@##;''+'+;+##@@#+''#@##'++;,.,;#####+'''++########++':+#@@@@@@@
#########''######@@#########@@@@@@@@@@@@#+##@@@#+;'+'++'''++#@###+;:##@########+++#+++'+''';##@@@@@@@
##@#####'++#################@##@@@@@@@@@@##++':.;+#+##+;''#@#;:;.,'####++++''''###+#########@##@@@@@#
@#######'##++++++#############@@@###+++#@##'#':;+,+####++'+;:+;:;;:;:'#####+#@@@@@#######@@#@@@#@@@@@
######################+#########++++++#####+;,..;;'#@##++'';;;,.,,'+++++++###@@@@@@@@@@@@@@@@@@@@@@@@
@@##@###############@##############@####@@##';;;'+####++;;'';:,,,,':+#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
###@@@############@@@##############@@@#@###++;'+######;;;,;;;::..'+####@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@#@@###########@@@#######@####+#@@@@@@#@######@@###';;:;:;;;;'#######@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@###########@@@#@@########+#####@@@@@###@@@####+;;;;;';';''';'''+###@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@#@@@@#########@@@@@@@@#@######+##+#@@@@@###@#@@@###+;:,.'''';'+'+##+'##+#@####@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@######@#@@@#@#########+#++##+#@@#####@@####+;::,..:+;;:.`;'#+#+##+'+''#++++@@@@@@@@@@@@@@@@@
@@@#@#@@######@@#@@@@#++++''++####+######@@########++';...,,:,,:;;''+'##@#++'''+''+###@@@@@@@@@@@@@@@
@@@@@@@@@##@@@##@#@########+''##@#@######@@####++++#+';:,...``,.;:';';+#####+'+'''''###@@@@@@@@@@@@@@
#######################+'++++''+###@####@###++#+;:,:,.`   ````.::;;;:+#######+++++'+++#+#@@@@@@@@@@@@
#################+###+++++'+'''+++'##@######+';;;:;::,`   ```,,,::;,:####+'+##++';;'''++###@@@@@@@@@@
@@@@@@@@@@@@@@##+###+++'+'+''++#++'+##@@##+#'+;::;,:.```  ``...,:,.;####'+#+'+''+++';;'+'+######@@@@#
#@@@@@@@@@@@@##+###+++#+####++#+++#+++##@@#+;':;,,,.``` ` ` ``.:.:'###;'+';+'########+'''+++':;'+####
@@@@@@@@@@@#############++++++##++++++###@@#+;,'::.`,`  .  .`:.::,`::.,';'''#####,,,,`,'+''++;';;'+##
#@@@@@@@#######+##+###+#####+++####++###@#'.::;',::.:`````.:`.::'.;+##,.:;'+###'.:;;:,,,'+'++''+''++#
@@@@@@@#++''++++#####+#####+##++++#######+,;+#+:;+:,.`;`..`;:;+#;.;+###..;;###+;;##++;;,.'''++'''''+#
@@@@@##++++''++######@@@@@@@@##++'+#@##@#;.;##'.,+''';';';;';,.....''##.`:;#++;'####''':;''''++'''''+
@@@@###++++++###+####@@@@#+###@#++'+#@###;.''';:::;';+';#''+::;;'+;;##+.`:;+#+;#'##+++'';;++++++'''+'
@@@@######++####+###@@######+++##+##+@###'.;+;::',`;+':,...'++:,..`+##:`.;''+'+####+++;;+:'+++'''';;'
@@@@@#######@##++####@#@####++#####+'+@+#+:`'+;,'++;+#''#+'+;,:;++###+` ,;+'':+####+':;':'+++##+'+';;
###@#######@@@###+#@@##@###+++#++@#+'+##++',.',,,.,+';..```.;++::,:+'` .;'+';'##'++#+',,;++++####+'++
+++#######@@@##@####@#@@##+++++;#@@#;';##++'. ;'''+++#++####+;.:'++,``,,+;+;:,+####+'';;'+'+###@###''
+''++####@@@@@@@@#####@####+##'+@@#'':;#+##+',` ,+,'+:.`````.+'+,.`,:;:.``..;###+#++':::;'+####@@@@@#"""


_PilotStackEntry = namedtuple('_PilotStackEntry', ['request', 'context', 'data'])


@implements_to_string
class Pilot(ObjectExposer):
    """Request manager singleton"""

    _local = local()
#    console = Console()  # Console is thread safe

    def __init__(self):
        try:
            with io.open(os.path.expanduser("~/.moyarc"), 'rt') as f:
                self.moyarc = settings.SettingsContainer.read_from_file(f)
        except IOError:
            self.moyarc = settings.SettingsContainer()
        self.console = Console(nocolors=not self.moyarc.get_bool('console', 'color', True))
        super(Pilot, self).__init__()

    def manage_request(self, request, context):
        self._stack.append(_PilotStackEntry(request, context, {}))
        return self

    def manage(self, context):
        self._stack.append(_PilotStackEntry(None, context, {}))
        return self

    def throw(self, type, msg, diagnosis=None, info=None):
        raise MoyaException(type, msg, diagnosis=diagnosis, info=info)

    @property
    def request(self):
        try:
            return self._stack[-1].request
        except IndexError:
            return None

    @property
    def context(self):
        try:
            return self._stack[-1].context
        except IndexError:
            return None

    @property
    def data(self):
        try:
            return self._stack[-1].data
        except IndexError:
            return None

    def __moyaconsole__(self, console):
        console.text(_ascii_pilot)

    def __str__(self):
        return "<pilot>"

    def __repr__(self):
        return "<pilot>"

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stack.pop()
        # import objgraph
        # objgraph.show_most_common_types(limit=20)
        # contexts= objgraph.by_type('moya.context.context.Context')
        # print(contexts)

    _stack = _LocalAttribute("stack", list)
    service = _LocalAttribute("service", dict)
