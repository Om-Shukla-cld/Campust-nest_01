from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user, get_current_user_optional
from ..database import get_db

router = APIRouter(prefix="/community", tags=["community"])


def _group_out(db: Session, g: models.CommunityGroup, user: Optional[models.User]) -> dict:
    d = schemas.GroupOut.model_validate(g).model_dump()
    d["member_count"] = db.query(func.count(models.GroupMember.id)).filter(models.GroupMember.group_id == g.id).scalar() or 0
    d["post_count"] = (
        db.query(func.count(models.CommunityPost.id))
        .filter(models.CommunityPost.group_id == g.id, models.CommunityPost.is_hidden == False)  # noqa: E712
        .scalar()
        or 0
    )
    d["is_member"] = bool(
        user
        and db.query(models.GroupMember)
        .filter(models.GroupMember.group_id == g.id, models.GroupMember.user_id == user.id)
        .first()
    )
    return d


def _post_out(p: models.CommunityPost, with_comments: bool = False) -> dict:
    d = schemas.PostOut.model_validate(p).model_dump()
    d["author"] = schemas.AuthorBrief.model_validate(p.author).model_dump() if p.author else None
    d["comment_count"] = len(p.comments)
    if with_comments:
        d["comments"] = [
            {
                **schemas.CommentOut.model_validate(c).model_dump(),
                "author": schemas.AuthorBrief.model_validate(c.author).model_dump() if c.author else None,
            }
            for c in p.comments
        ]
    return d


@router.get("/groups", response_model=List[schemas.GroupOut])
def list_groups(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    user: Optional[models.User] = Depends(get_current_user_optional),
):
    q = db.query(models.CommunityGroup)
    if category:
        q = q.filter(models.CommunityGroup.category == category)
    return [_group_out(db, g, user) for g in q.order_by(models.CommunityGroup.id).all()]


@router.get("/groups/{group_id}", response_model=schemas.GroupOut)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    user: Optional[models.User] = Depends(get_current_user_optional),
):
    g = db.query(models.CommunityGroup).filter(models.CommunityGroup.id == group_id).first()
    if not g:
        raise HTTPException(404, "Group not found")
    return _group_out(db, g, user)


@router.post("/groups/{group_id}/join", response_model=schemas.Message)
def join_group(
    group_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    g = db.query(models.CommunityGroup).filter(models.CommunityGroup.id == group_id).first()
    if not g:
        raise HTTPException(404, "Group not found")
    exists = (
        db.query(models.GroupMember)
        .filter(models.GroupMember.group_id == group_id, models.GroupMember.user_id == user.id)
        .first()
    )
    if exists:
        db.delete(exists)
        db.commit()
        return schemas.Message(message="Left group", data={"joined": False})
    db.add(models.GroupMember(group_id=group_id, user_id=user.id))
    db.commit()
    return schemas.Message(message="Joined group", data={"joined": True})


@router.get("/groups/{group_id}/posts", response_model=List[schemas.PostOut])
def group_posts(
    group_id: int,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    posts = (
        db.query(models.CommunityPost)
        .filter(models.CommunityPost.group_id == group_id, models.CommunityPost.is_hidden == False)  # noqa: E712
        .order_by(models.CommunityPost.created_at.desc())
        .limit(limit)
        .all()
    )
    return [_post_out(p) for p in posts]


@router.get("/feed", response_model=List[schemas.PostOut])
def feed(limit: int = Query(30, le=200), db: Session = Depends(get_db)):
    """Latest posts across all groups (home feed)."""
    posts = (
        db.query(models.CommunityPost)
        .filter(models.CommunityPost.is_hidden == False)  # noqa: E712
        .order_by(models.CommunityPost.created_at.desc())
        .limit(limit)
        .all()
    )
    return [_post_out(p) for p in posts]


@router.post("/posts", response_model=schemas.PostOut, status_code=201)
def create_post(
    body: schemas.PostCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not db.query(models.CommunityGroup).filter(models.CommunityGroup.id == body.group_id).first():
        raise HTTPException(404, "Group not found")
    post = models.CommunityPost(
        group_id=body.group_id,
        user_id=user.id,
        title=body.title,
        content=body.content,
        tags=body.tags,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return _post_out(post)


@router.get("/posts/{post_id}", response_model=schemas.PostDetail)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.CommunityPost).filter(models.CommunityPost.id == post_id).first()
    if not post or post.is_hidden:
        raise HTTPException(404, "Post not found")
    return _post_out(post, with_comments=True)


@router.post("/posts/{post_id}/like", response_model=schemas.Message)
def like_post(
    post_id: int, _: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    post = db.query(models.CommunityPost).filter(models.CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    post.likes = (post.likes or 0) + 1
    db.commit()
    return schemas.Message(message="Liked", data={"likes": post.likes})


@router.post("/posts/{post_id}/comments", response_model=schemas.CommentOut, status_code=201)
def add_comment(
    post_id: int,
    body: schemas.CommentCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(models.CommunityPost).filter(models.CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    c = models.PostComment(post_id=post_id, user_id=user.id, content=body.content)
    db.add(c)
    db.commit()
    db.refresh(c)
    d = schemas.CommentOut.model_validate(c).model_dump()
    d["author"] = schemas.AuthorBrief.model_validate(user).model_dump()
    return d


@router.post("/posts/{post_id}/flag", response_model=schemas.Message)
def flag_post(
    post_id: int, _: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    post = db.query(models.CommunityPost).filter(models.CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    post.is_flagged = True
    db.commit()
    return schemas.Message(message="Post reported to moderators")


@router.delete("/posts/{post_id}", response_model=schemas.Message)
def delete_post(
    post_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    post = db.query(models.CommunityPost).filter(models.CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    if post.user_id != user.id and user.role != "moderator":
        raise HTTPException(403, "Not allowed")
    db.delete(post)
    db.commit()
    return schemas.Message(message="Post deleted")
