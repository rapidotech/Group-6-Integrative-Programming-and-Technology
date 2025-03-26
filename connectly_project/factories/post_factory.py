from posts.models import Post
from django.core.exceptions import ValidationError

class PostFactory:
    @staticmethod
    def create_post(post_type, title, content='', metadata=None):
        """
        Creates a validated post with type-specific requirements
        Args:
            post_type: One of Post.POST_TYPES keys ('text', 'image', 'video')
            title: Post title
            content: Post content
            metadata: Dictionary of additional data
        Returns:
            Post instance
        Raises:
            ValueError: If validation fails
        """
        metadata = metadata or {}
        
        # Validate post type
        valid_types = dict(Post.POST_TYPES).keys()
        if post_type not in valid_types:
            raise ValueError(f"Invalid post type. Must be one of: {', '.join(valid_types)}")

        # Type-specific validations
        if post_type == 'image':
            if 'file_size' not in metadata:
                raise ValueError("Image posts require 'file_size' in metadata")
        elif post_type == 'video':
            if 'duration' not in metadata:
                raise ValueError("Video posts require 'duration' in metadata")

        # Create and return the post
        return Post.objects.create(
            title=title,
            content=content,
            post_type=post_type,
            metadata=metadata
        )