export function EpisodeCard({ episode }) {
  return (
    <article className="episode-card">
      <h2>{episode.title}</h2>
      <p className="waveform">Now playing: merged pull request #{episode.pr}</p>
      <button className="play">Play episode</button>
    </article>
  );
}
