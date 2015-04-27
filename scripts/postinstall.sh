manage="${VENV}/bin/python ${INSTALLDIR}/${REPO}/manage.py"

cd "${INSTALLDIR}/${REPO}/"

$manage syncdb --noinput --migrate
$manage collectstatic --noinput

sudo supervisorctl restart actionforwomen_mobi actionforwomen_celery
