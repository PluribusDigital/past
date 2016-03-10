app.controller('RankController', function ($scope, $http, $location, $routeParams) {
    /************************************************************************************************
     * Properties
     */
    $scope.words = $routeParams.words;

    $scope.model = []
    $scope.columns = [
        { 'name': 'score', 'title': 'Score', 'show': true, 'type': 'float' },
        { 'name': 'count', 'title': 'Count', 'show': true, 'type': 'int' },
        { 'name': 'title', 'title': 'Title', 'show': true, 'type': 'string' },
    ]

    $scope.corpora = [''];
    $scope.limits = [10, 20, 25, 50, 100];

    /************************************************************************************************
    * Data Model Methods
    */

    $scope.onModelLoaded = function (data) {
        $scope.model = [];

        if (data == null) {
            return;
        }

        // Convert to the model
        angular.forEach(data, function (d) {
            var row = {
                'score': d.score,
                'count': d.count,
                'title': d.entry.title,
                'link': d.entry.links[0].href.replace('/api/v1/', '/')
            };
            $scope.model.push(row);
        });

    }

    $scope.onCorpusLoaded = function (data) {
        $scope.corpora = [''];

        if (data == null) {
            return;
        }

        // Convert to the model
        angular.forEach(data, function (d) {
            $scope.corpora.push(d.title);
        });
    }

    /************************************************************************************************
     * Table Members
     */

    $scope.orderBy = '-score';

    $scope.setOrder = function (orderBy) {
        if (orderBy === $scope.orderBy)
            $scope.orderBy = '-' + orderBy;  // Reverse the sort
        else
            $scope.orderBy = orderBy;
    }

    /************************************************************************************************
     * Actions
     */

    $scope.refresh = function () {
        var params = {};
        if ($scope.field != 'lemma')
            params.field = $scope.field;
        if ($scope.limit != 10)
            params.limit = $scope.limit;
        if ($scope.filterCorpus != '')
            params.corpus = $scope.filterCorpus;

        var url = $location.path();
        var query = $.param(params);
        if (query !== '') {
            url = url + '?' + query;
        }

        $location.url(url);
    };

    /************************************************************************************************
     * Methods
     */

    $scope.buildBaseApiUrl = function () {
        url = 'http://' + $location.host() + ':' + $location.port() + '/api/v1';
        return url;
    };

    $scope.buildUrl = function () {
        query = $.param($location.search());

        url = 'http://' + $location.host() + ':' + $location.port();
        url = url + '/api/v1/rank/' + $scope.words;
        if (query !== '') {
            url = url + '?' + query
        }

        return url;
    };

    $scope.initOptions = function () {
        var query = $location.search();

        $scope.limit = ('limit' in query) ? parseInt(query['limit']) : 10;
        $scope.filterCorpus = ('corpus' in query) ? query['corpus'] : '';
        $scope.field = ('field' in query) ? query['field'] : 'lemma';
    };

    $scope.request = function (url, callback) {
        $http.get(url).then(
            function (response) { callback(response.data) },
            function (response) { alert(response.status) }
            );
    };

    /************************************************************************************************
     * Initialization
     */

    $scope.initOptions();
    $scope.apiBaseUrl = $scope.buildBaseApiUrl();

    $scope.request($scope.buildUrl(), $scope.onModelLoaded);
    $scope.request($scope.apiBaseUrl + '/corpus', $scope.onCorpusLoaded);
});