import Header from "../components/Header";
import { Link, useNavigate} from 'react-router-dom';

function Home() {
    return (
      <div>
      <Header />
      <h2 className="text-3xl text-center py-6">Analyze your Messenger conversations!</h2>
      <div className="flex items-center justify-center">
          <Link to="/analyze" className="px-6 py-3 text-lg font-semibold bg-blue-500 text-white rounded-xl hover:bg-blue-700">Analyze</Link>
      </div>
      <div className="content-center text-center items-center justify-center py-6">
        <div>
          <h2 id="how-to-download-facebook-messages-data" className="text-3xl font-semibold">
            How to download Facebook Messages Data
          </h2>
          <div className="mt-6">
            <p>
              Visit{" "}
              <a
                href="https://accountscenter.facebook.com/info_and_permissions/dyi"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500"
              >
                https://accountscenter.facebook.com/info_and_permissions/dyi
              </a>{" "}
              and log in to your Facebook account if required. Click "Download or transfer information" then
              "Specific types of information"
            </p>
            <div className="flex justify-center items-center pt-2 space-x-4">
              <img src="/img/dlfb1.JPG" alt="alt text" className="h-96" />
              <img src="/img/dlfb2.JPG" alt="alt text" className="h-96" />
            </div>
          </div>
          <div className="mt-6">
            <p>
              In the next screen, only check the "Messages" box and click "Next". Then select "Download to device" and
              click "Next" again.
            </p>
            <div className="flex justify-center items-center pt-2 space-x-4">
              <img src="/img/dlfb3.JPG" alt="alt text" className="h-96" />
              <img src="/img/dlfb4.JPG" alt="alt text" className="h-96" />
            </div>
          </div>
          <div className="mt-6">
            <p>
              Choose your date range, enter the email address you wish to be notified at, set the format to JSON, and set
              the media quality to low (allows for fast download as we don't access the media files).
            </p>
            <div className="flex justify-center items-center pt-2">
              <img src="/img/dlfb5.JPG" alt="alt text" className="h-96" />
            </div>
            <p>
              After the download is ready, you will be notified. Download the zip file. The data is now ready to be fed to
              the program!
            </p>
          </div>
        </div>

        <div className="mt-12">
          <h2 id="available-visualizations" className="text-3xl font-semibold">
            Available Visualizations
          </h2>
          <h3 id="top-10-n-most-messaged" className="mt-6 text-xl">
            Top 10 (n) Most Messaged
          </h3>
          <p>Identifies who you have exchanged the most messages with</p>
          <div className="flex justify-center items-center pt-2 space-x-4">
            <img src="/img/topn.png" alt="alt text" />
          </div>
          <h3 id="messages-over-time-sent-and-received-" className="mt-6 text-xl">
            Messages over time (sent and received)
          </h3>
          <p>
            Shows activity over time. May be able to identify cyclical patterns or trends. Can also see the effect of
            certain events on your messaging habits (e.g. Do I talk to more people during a global pandemic?)
          </p>
          <div className="flex justify-center items-center pt-2 space-x-4">
            <img src="/img/msg_v_time.PNG" alt="alt text" />
          </div>
          <h3 id="messages-over-time-with-a-specific-contact-sent-and-received-" className="mt-6 text-xl">
            Messages over time with a specific contact (sent and received)
          </h3>
          <p>Similar to above.</p>
          <div className="flex justify-center items-center pt-2 space-x-4">
            <img src="/img/msg_v_time_contact.png" alt="alt text" />
          </div>
          <h3 id="hourly-distribution-of-sent-messages" className="mt-6 text-xl">
            Hourly Distribution of sent messages
          </h3>
          <p>
            Provides information on when you are most likely to reply. Can be used to identify unhealthy patterns or
            habits.
          </p>
          <div className="flex justify-center items-center pt-2 space-x-4">
            <img src="/img/msg_dist.JPG" alt="alt text" />
          </div>
          <h3 id="word-spectrum" className="mt-6 text-xl">
            Word spectrum
          </h3>
          <p>
            For a specific contact, identify which words you are more likely to type opposed to your contact.
          </p>
          <div className="flex justify-center items-center pt-2 space-x-4">
            <img src="/img/wordspectrum.PNG" alt="alt text" />
          </div>
        </div>
      </div>
      </div>
    );
}

export default Home;