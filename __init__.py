import os, logging
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
LOGGER = logging.getLogger("AjayVcStreamBot")

API_ID = int(os.getenv("API_ID", "35828291"))
API_HASH = os.getenv("API_HASH", "c025ee9d01d73b9d738d4f3e5e6137e2")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8628227065:AAGYRzHDTCchjF3X0TPXaeQ_J_RNLATuPDc")
SESSION_STRING = os.getenv("SESSION_STRING", "BQIiskMANNY39qPj2BDNIyqXJTnhSHx-xKFQSQrJyRj0gi2RCX8_FOpVzh6SVNOaRw3DSINTyoPx1ScsPTDlKJ20EFG-CA606H8-ZHD-wBdvbbx11Ln1wFsOf5pkf97YVrxxaprBg2ibATvEQmm4Uc0ViBcBUdEFPbskK1IubAkXKWf7jixqWT__Kpw-ACQu5-7SOYgJCpL9qML7a_MHAaB3l6lSA5HBV_N6xk1lsDfP3ggw12D4VXMGx9xC715T0dRbJNMSmmNs5nZRblxK1Ut0uJL1xRBd5i4w8us7NNQZ9SRQjaPwQfdmrpeEkS94TE70UwnqEO9SsGi55SNqX6qTq9AjBgAAAAICSEv5AQ")
OWNER_ID = int(os.getenv("OWNER_ID", "7953454559"))

assert API_ID and API_HASH and BOT_TOKEN and SESSION_STRING, "Missing required env vars"
