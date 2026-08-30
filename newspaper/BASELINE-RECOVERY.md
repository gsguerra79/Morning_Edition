# Source and runtime recovery boundary

GitHub and runtime backups solve different recovery problems.

## GitHub recovers

- application and deployment code;
- tests and CI;
- sanitized sample configuration;
- product and execution documentation;
- decision and problem history recorded in the execution plan.

## GitHub deliberately does not recover

- credentials or `.env` files;
- live source inventories or owner-specific configuration;
- read, dismiss, save, history, or learned-affinity state;
- generated digests, embeddings, run history, or edition archives;
- internal addresses and operator-specific infrastructure records.

Those require a separately secured runtime backup. Never upload an unencrypted
runtime archive to a public GitHub repository or release.

## Create and verify a local runtime backup

Choose a new explicit child directory under the repository's ignored
`backups/` directory:

```sh
./scripts/backup-runtime.sh /absolute/path/to/repository/backups/YYYYMMDDTHHMMSSZ
./scripts/verify-runtime-backup.sh /absolute/path/to/repository/backups/YYYYMMDDTHHMMSSZ
```

The backup script pauses the production container only while capturing a
consistent archive and edition checksums. Verification checks the archive,
restores into a disposable Docker volume, compares every edition checksum, and
removes the disposable volume without mounting production state.
The archive checksum manifest references `runtime-data.tar` by basename so a
copied backup validates the copied archive, not its original location.

The verifier defaults to the clean-clone image tag
`morning-edition:recovery`. Set `RESTORE_IMAGE` only when deliberately
verifying with a different locally available image. The backup script defaults
to container `forge-daily`; set `FORGE_DAILY_CONTAINER` for another explicit
deployment name.

## Clean-clone source recovery

```sh
git clone git@github.com:gsguerra79/Morning_Edition.git
cd Morning_Edition/newspaper
python -m unittest -v test_editions.py test_baseline.py
docker compose config --quiet
docker compose -f docker-compose.shadow.yaml config --quiet
docker build -t morning-edition:recovery .
```

After source recovery passes, restore production state only under an approved
operator procedure: stop writers, verify the exact target volume, preserve the
current damaged state for diagnosis, verify the backup checksum, restore, start
the service, and compare edition/state evidence.

## Shadow execution

`docker-compose.shadow.yaml` is a standalone Compose project. It binds only to
loopback, stores application data in a dedicated shadow volume, uses paths below
`/shadow`, and disables automatic edition deadlines. It never mounts the
production volume.
