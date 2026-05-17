FROM ruby:3.4

WORKDIR /home/app

COPY Gemfile* ./

RUN gem install bundler:2.6.3 && bundle install

COPY . .

CMD [ "bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0" ]