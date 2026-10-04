import rss from '@astrojs/rss';
import { getPublishedPosts } from '../lib/posts';
import { site } from '../site';

export async function GET(context: { site: URL }) {
  const posts = await getPublishedPosts();
  return rss({
    title: site.title,
    description: site.description,
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.published,
      link: `/posts/${post.id}/`,
      categories: post.data.tags,
    })),
  });
}
